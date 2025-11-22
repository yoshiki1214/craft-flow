"""全銀フォーマット変換ユーティリティ

全国銀行協会統一フォーマット（全銀フォーマット）への変換処理を提供
"""

from datetime import datetime
from typing import List, Dict, Optional, Tuple
import pandas as pd


class ZenginFormatError(Exception):
    """全銀フォーマット変換エラー"""

    pass


class ZenginConverter:
    """全銀フォーマット変換クラス"""

    # 全銀フォーマットのレコード長（総合振込フォーマット）
    RECORD_LENGTH = 120

    # 全角カナ→半角カナ変換テーブル
    ZENKAKU_TO_HANKAKU = {
        "ア": "ｱ",
        "イ": "ｲ",
        "ウ": "ｳ",
        "エ": "ｴ",
        "オ": "ｵ",
        "カ": "ｶ",
        "キ": "ｷ",
        "ク": "ｸ",
        "ケ": "ｹ",
        "コ": "ｺ",
        "サ": "ｻ",
        "シ": "ｼ",
        "ス": "ｽ",
        "セ": "ｾ",
        "ソ": "ｿ",
        "タ": "ﾀ",
        "チ": "ﾁ",
        "ツ": "ﾂ",
        "テ": "ﾃ",
        "ト": "ﾄ",
        "ナ": "ﾅ",
        "ニ": "ﾆ",
        "ヌ": "ﾇ",
        "ネ": "ﾈ",
        "ノ": "ﾉ",
        "ハ": "ﾊ",
        "ヒ": "ﾋ",
        "フ": "ﾌ",
        "ヘ": "ﾍ",
        "ホ": "ﾎ",
        "マ": "ﾏ",
        "ミ": "ﾐ",
        "ム": "ﾑ",
        "メ": "ﾒ",
        "モ": "ﾓ",
        "ヤ": "ﾔ",
        "ユ": "ﾕ",
        "ヨ": "ﾖ",
        "ラ": "ﾗ",
        "リ": "ﾘ",
        "ル": "ﾙ",
        "レ": "ﾚ",
        "ロ": "ﾛ",
        "ワ": "ﾜ",
        "ヲ": "ｦ",
        "ン": "ﾝ",
        "ガ": "ｶﾞ",
        "ギ": "ｷﾞ",
        "グ": "ｸﾞ",
        "ゲ": "ｹﾞ",
        "ゴ": "ｺﾞ",
        "ザ": "ｻﾞ",
        "ジ": "ｼﾞ",
        "ズ": "ｽﾞ",
        "ゼ": "ｾﾞ",
        "ゾ": "ｿﾞ",
        "ダ": "ﾀﾞ",
        "ヂ": "ﾁﾞ",
        "ヅ": "ﾂﾞ",
        "デ": "ﾃﾞ",
        "ド": "ﾄﾞ",
        "バ": "ﾊﾞ",
        "ビ": "ﾋﾞ",
        "ブ": "ﾌﾞ",
        "ベ": "ﾍﾞ",
        "ボ": "ﾎﾞ",
        "パ": "ﾊﾟ",
        "ピ": "ﾋﾟ",
        "プ": "ﾌﾟ",
        "ペ": "ﾍﾟ",
        "ポ": "ﾎﾟ",
        "ァ": "ｧ",
        "ィ": "ｨ",
        "ゥ": "ｩ",
        "ェ": "ｪ",
        "ォ": "ｫ",
        "ャ": "ｬ",
        "ュ": "ｭ",
        "ョ": "ｮ",
        "ッ": "ｯ",
        "ー": "ｰ",
        "、": "､",
        "。": "｡",
        "・": "･",
        "「": "｢",
        "」": "｣",
        "　": " ",  # 全角スペース→半角スペース
    }

    # データ・レコードのフィールド定義（総合振込フォーマット準拠）
    FIELD_DEFINITIONS = {
        "data_type": {"pos": 0, "length": 1, "default": "2"},  # データ区分: 2=データ
        "bank_code": {"pos": 1, "length": 4, "fill": "0", "align": "right"},  # 被仕向銀行番号
        "bank_name": {"pos": 5, "length": 15, "fill": " ", "align": "left"},  # 被仕向銀行名
        "branch_code": {"pos": 20, "length": 3, "fill": "0", "align": "right"},  # 被仕向支店番号
        "branch_name": {"pos": 23, "length": 15, "fill": " ", "align": "left"},  # 被仕向支店名
        "clearing_house": {"pos": 38, "length": 4, "fill": "0", "align": "right"},  # 手形交換所番号
        "account_type": {"pos": 42, "length": 1, "default": "1"},  # 預金種目: 1=普通, 2=当座
        "account_number": {"pos": 43, "length": 7, "fill": "0", "align": "right"},  # 口座番号
        "recipient_name": {"pos": 50, "length": 30, "fill": " ", "align": "left"},  # 受取人名
        "amount": {"pos": 80, "length": 10, "fill": "0", "align": "right"},  # 振込金額
        "new_code": {"pos": 90, "length": 1, "default": "1"},  # 新規コード
        "customer_code1": {"pos": 91, "length": 10, "fill": " ", "align": "left"},  # 顧客コード1
        "customer_code2": {"pos": 101, "length": 10, "fill": " ", "align": "left"},  # 顧客コード2
        "transfer_type": {"pos": 111, "length": 1, "default": "0"},  # 振込指定区分
        "identification": {"pos": 112, "length": 1, "fill": " ", "align": "left"},  # 識別表示
        "dummy": {"pos": 113, "length": 7, "fill": " ", "align": "left"},  # ダミー
    }

    @classmethod
    def _to_hankaku_kana(cls, text: str) -> str:
        """
        全角カナを半角カナに変換

        Args:
            text: 変換対象の文字列

        Returns:
            半角カナに変換された文字列
        """
        result = []
        for char in text:
            if char in cls.ZENKAKU_TO_HANKAKU:
                result.append(cls.ZENKAKU_TO_HANKAKU[char])
            else:
                result.append(char)
        return "".join(result)

    @staticmethod
    def _pad_string(
        value: str, length: int, fill_char: str = " ", align: str = "left", encoding: str = "shift_jis"
    ) -> str:
        """
        文字列を指定バイト長に調整（パディング）- Shift-JIS対応

        Args:
            value: パディング対象の文字列
            length: 目標バイト長
            fill_char: 埋め込み文字
            align: 配置方向（'left'=左寄せ、'right'=右寄せ）
            encoding: エンコーディング（デフォルト: shift_jis）

        Returns:
            パディング済み文字列（指定バイト長）
        """
        # 文字列をバイト列に変換
        value_bytes = value.encode(encoding, errors="replace")
        fill_bytes = fill_char.encode(encoding, errors="replace")

        # バイト長を確認
        current_length = len(value_bytes)

        # バイト長が目標長を超える場合は切り詰める
        if current_length > length:
            # 指定バイト数で切り詰め、デコードエラーを避けるために調整
            truncated = value_bytes[:length]
            # 末尾が不完全なマルチバイト文字になっていないか確認
            try:
                result = truncated.decode(encoding)
            except UnicodeDecodeError:
                # 末尾を1バイトずつ削って再試行
                for i in range(1, 3):
                    try:
                        result = truncated[:-i].decode(encoding)
                        # 削った分をスペースで埋める
                        result += " " * i
                        break
                    except UnicodeDecodeError:
                        continue
            return result

        # バイト長が目標長より短い場合はパディング
        padding_needed = length - current_length
        padding = fill_bytes * padding_needed

        if align == "right":
            result_bytes = padding + value_bytes
        else:
            result_bytes = value_bytes + padding

        return result_bytes.decode(encoding)

    @staticmethod
    def _validate_numeric(value: str, field_name: str, max_digits: Optional[int] = None) -> str:
        """
        数値フィールドの検証

        Args:
            value: 検証対象の値
            field_name: フィールド名（エラーメッセージ用）
            max_digits: 最大桁数

        Returns:
            検証済みの文字列

        Raises:
            ZenginFormatError: 検証失敗時
        """
        # NoneやNaNの処理
        if pd.isna(value) or value is None:
            raise ZenginFormatError(f"{field_name}が空です")

        # 文字列に変換
        str_value = str(value).strip()

        # 数値チェック
        if not str_value.isdigit():
            raise ZenginFormatError(f"{field_name}は数値である必要があります: {value}")

        # 桁数チェック
        if max_digits and len(str_value) > max_digits:
            raise ZenginFormatError(f"{field_name}の桁数が超過しています: {value} (最大: {max_digits}桁)")

        return str_value

    @classmethod
    def validate_customer_data(cls, row: Dict) -> Tuple[bool, List[str]]:
        """
        顧客データのバリデーション

        Args:
            row: 顧客データの辞書

        Returns:
            (検証結果, エラーメッセージリスト)
        """
        errors = []

        # 必須フィールドのチェック
        required_fields = ["bank_code", "branch_code", "account_number", "recipient_name", "amount"]
        for field in required_fields:
            if field not in row or pd.isna(row[field]):
                errors.append(f"{field}が必須です")

        # 銀行コードの検証
        if "bank_code" in row and not pd.isna(row["bank_code"]):
            try:
                bank_code = cls._validate_numeric(row["bank_code"], "銀行コード", 4)
                if len(bank_code) > 4:
                    errors.append("銀行コードは4桁以内である必要があります")
            except ZenginFormatError as e:
                errors.append(str(e))

        # 支店コードの検証
        if "branch_code" in row and not pd.isna(row["branch_code"]):
            try:
                branch_code = cls._validate_numeric(row["branch_code"], "支店コード", 3)
                if len(branch_code) > 3:
                    errors.append("支店コードは3桁以内である必要があります")
            except ZenginFormatError as e:
                errors.append(str(e))

        # 口座番号の検証
        if "account_number" in row and not pd.isna(row["account_number"]):
            try:
                account_number = cls._validate_numeric(row["account_number"], "口座番号", 7)
                if len(account_number) > 7:
                    errors.append("口座番号は7桁以内である必要があります")
            except ZenginFormatError as e:
                errors.append(str(e))

        # 口座種別の検証
        if "account_type" in row and not pd.isna(row["account_type"]):
            account_type = str(row["account_type"]).strip()
            # 「普通」「当座」という文字列も許可し、後で変換
            if account_type not in ["1", "2", "普通", "当座"]:
                errors.append("口座種別は1（普通）または2（当座）である必要があります")

        # 振込金額の検証
        if "amount" in row and not pd.isna(row["amount"]):
            try:
                # 数値の場合はそのまま、文字列の場合は変換
                if isinstance(row["amount"], (int, float)):
                    amount_value = int(row["amount"])
                else:
                    amount_str = str(row["amount"]).replace(",", "").strip()
                    amount_value = int(float(amount_str))

                if amount_value <= 0:
                    errors.append("振込金額は0より大きい必要があります")
            except (ValueError, TypeError):
                errors.append(f"振込金額の形式が不正です: {row['amount']}")

        # 受取人名の検証（半角カナ30バイト）
        if "recipient_name" in row and not pd.isna(row["recipient_name"]):
            recipient_name = str(row["recipient_name"]).strip()
            if len(recipient_name) == 0:
                errors.append("受取人名が空です")
            else:
                # 半角カナに変換してバイト数をチェック
                recipient_name_hankaku = cls._to_hankaku_kana(recipient_name)
                recipient_name_bytes = recipient_name_hankaku.encode("shift_jis", errors="replace")
                if len(recipient_name_bytes) > 30:
                    errors.append(f"受取人名が長すぎます（最大30バイト）: {recipient_name}")

        return len(errors) == 0, errors

    @classmethod
    def convert_row_to_record(cls, row: Dict, requester_code: str = "", requester_name: str = "") -> str:
        """
        顧客データの1行を全銀フォーマットのデータ・レコードに変換（総合振込フォーマット準拠）

        Args:
            row: 顧客データの辞書
            requester_code: 依頼人コード（オプション）
            requester_name: 依頼人名（オプション）

        Returns:
            全銀フォーマットの120バイト固定長データ・レコード

        Raises:
            ZenginFormatError: 変換エラー時
        """
        # バリデーション
        is_valid, errors = cls.validate_customer_data(row)
        if not is_valid:
            raise ZenginFormatError(f"データ検証エラー: {', '.join(errors)}")

        # レコードをバイト配列として初期化（120バイト、スペースで埋める）
        record_bytes = bytearray(b" " * cls.RECORD_LENGTH)

        # 各フィールドを設定（総合振込データ・レコード仕様）
        defs = cls.FIELD_DEFINITIONS

        # 1. データ区分: 2
        record_bytes[defs["data_type"]["pos"]] = ord(defs["data_type"]["default"])

        # 2. 被仕向銀行番号（4桁、右寄せゼロ埋め）
        bank_code = cls._validate_numeric(row["bank_code"], "銀行コード", 4)
        bank_code_str = cls._pad_string(bank_code, 4, "0", "right")
        bank_code_bytes = bank_code_str.encode("shift_jis")
        pos = defs["bank_code"]["pos"]
        record_bytes[pos : pos + len(bank_code_bytes)] = bank_code_bytes

        # 3. 被仕向銀行名（15バイト、左寄せスペース埋め、半角カナ）
        bank_name = str(row.get("bank_name", "")).strip()
        bank_name_hankaku = cls._to_hankaku_kana(bank_name)  # 半角カナに変換
        bank_name_str = cls._pad_string(bank_name_hankaku, 15, " ", "left")
        bank_name_bytes = bank_name_str.encode("shift_jis")
        pos = defs["bank_name"]["pos"]
        record_bytes[pos : pos + 15] = bank_name_bytes[:15]

        # 4. 被仕向支店番号（3桁、右寄せゼロ埋め）
        branch_code = cls._validate_numeric(row["branch_code"], "支店コード", 3)
        branch_code_str = cls._pad_string(branch_code, 3, "0", "right")
        branch_code_bytes = branch_code_str.encode("shift_jis")
        pos = defs["branch_code"]["pos"]
        record_bytes[pos : pos + len(branch_code_bytes)] = branch_code_bytes

        # 5. 被仕向支店名（15バイト、左寄せスペース埋め、半角カナ）
        branch_name = str(row.get("branch_name", "")).strip()
        branch_name_hankaku = cls._to_hankaku_kana(branch_name)  # 半角カナに変換
        branch_name_str = cls._pad_string(branch_name_hankaku, 15, " ", "left")
        branch_name_bytes = branch_name_str.encode("shift_jis")
        pos = defs["branch_name"]["pos"]
        record_bytes[pos : pos + 15] = branch_name_bytes[:15]

        # 6. 手形交換所番号（4桁、右寄せゼロ埋め）
        clearing_house = str(row.get("clearing_house", "0000")).strip()
        clearing_house_str = cls._pad_string(clearing_house, 4, "0", "right")
        clearing_house_bytes = clearing_house_str.encode("shift_jis")
        pos = defs["clearing_house"]["pos"]
        record_bytes[pos : pos + len(clearing_house_bytes)] = clearing_house_bytes

        # 7. 預金種目（1桁）: 1=普通、2=当座、4=貯蓄、9=その他
        account_type = str(row.get("account_type", "1")).strip()
        if account_type == "普通" or account_type.lower() == "futsu":
            account_type = "1"
        elif account_type == "当座" or account_type.lower() == "toza":
            account_type = "2"
        elif account_type == "貯蓄" or account_type.lower() == "chochiku":
            account_type = "4"
        elif account_type not in ["1", "2", "4", "9"]:
            account_type = "1"  # デフォルトは普通
        record_bytes[defs["account_type"]["pos"]] = ord(account_type)

        # 8. 口座番号（7桁、右寄せゼロ埋め）
        account_number = cls._validate_numeric(row["account_number"], "口座番号", 7)
        account_number_str = cls._pad_string(account_number, 7, "0", "right")
        account_number_bytes = account_number_str.encode("shift_jis")
        pos = defs["account_number"]["pos"]
        record_bytes[pos : pos + len(account_number_bytes)] = account_number_bytes

        # 9. 受取人名（30バイト、左寄せスペース埋め、半角カナ）
        recipient_name = str(row["recipient_name"]).strip()
        recipient_name_hankaku = cls._to_hankaku_kana(recipient_name)  # 半角カナに変換
        recipient_name_str = cls._pad_string(recipient_name_hankaku, 30, " ", "left")
        recipient_name_bytes = recipient_name_str.encode("shift_jis")
        pos = defs["recipient_name"]["pos"]
        record_bytes[pos : pos + 30] = recipient_name_bytes[:30]

        # 10. 振込金額（10桁、右寄せゼロ埋め）
        if isinstance(row["amount"], (int, float)):
            amount_value = int(row["amount"])
        else:
            amount_str_raw = str(row["amount"]).replace(",", "").strip()
            amount_value = int(float(amount_str_raw))

        amount_str = cls._pad_string(str(amount_value), 10, "0", "right")
        amount_bytes = amount_str.encode("shift_jis")
        record_bytes[defs["amount"]["pos"] : defs["amount"]["pos"] + len(amount_bytes)] = amount_bytes

        # 11. 新規コード（1桁）
        new_code = str(row.get("new_code", "1")).strip()
        if new_code not in ["1", "2"]:
            new_code = "1"
        record_bytes[defs["new_code"]["pos"]] = ord(new_code)

        # 12. 顧客コード1（10桁、左寄せスペース埋め）
        customer_code1 = str(row.get("customer_code1", "")).strip()
        customer_code1_str = cls._pad_string(customer_code1, 10, " ", "left")
        customer_code1_bytes = customer_code1_str.encode("shift_jis")
        pos = defs["customer_code1"]["pos"]
        record_bytes[pos : pos + 10] = customer_code1_bytes[:10]

        # 13. 顧客コード2（10桁、左寄せスペース埋め）
        customer_code2 = str(row.get("customer_code2", "")).strip()
        customer_code2_str = cls._pad_string(customer_code2, 10, " ", "left")
        customer_code2_bytes = customer_code2_str.encode("shift_jis")
        pos = defs["customer_code2"]["pos"]
        record_bytes[pos : pos + 10] = customer_code2_bytes[:10]

        # 14. 振込指定区分（1桁）
        transfer_type = str(row.get("transfer_type", "0")).strip()
        record_bytes[defs["transfer_type"]["pos"]] = ord(transfer_type)

        # 15. 識別表示（1桁、スペース）
        # 16. ダミー（7桁、スペース）は既にスペースで埋められている

        # バイト配列を文字列に変換
        return record_bytes.decode("shift_jis")

    @classmethod
    def create_header_record(cls, record_count: int, date: Optional[datetime] = None) -> str:
        """
        ヘッダー・レコードを作成（総合振込フォーマット準拠）

        Args:
            record_count: データレコード数
            date: 振込日（デフォルト: 今日）

        Returns:
            ヘッダーレコード（120バイト固定長）
        """
        if date is None:
            date = datetime.now()

        # レコードをバイト配列として初期化（120バイト、スペースで埋める）
        record_bytes = bytearray(b" " * cls.RECORD_LENGTH)

        # 1. データ区分: 1（ヘッダー）
        record_bytes[0] = ord("1")

        # 2. 種別コード: 21（総合振込）
        record_bytes[1:3] = b"21"

        # 3. コード区分: 0（JIS）
        record_bytes[3] = ord("0")

        # 4. 委託者コード（10桁、左寄せスペース埋め）
        requester_code = ""  # TODO: 適切な値を設定
        requester_code_str = cls._pad_string(requester_code, 10, " ", "left")
        requester_code_bytes = requester_code_str.encode("shift_jis")
        record_bytes[4:14] = requester_code_bytes[:10]

        # 5. 委託者名（40バイト、左寄せスペース埋め、半角カナ）
        requester_name = ""  # TODO: 適切な値を設定
        requester_name_hankaku = cls._to_hankaku_kana(requester_name)
        requester_name_str = cls._pad_string(requester_name_hankaku, 40, " ", "left")
        requester_name_bytes = requester_name_str.encode("shift_jis")
        record_bytes[14:54] = requester_name_bytes[:40]

        # 6. 振込日（4桁、MMDD）
        date_str = date.strftime("%m%d")
        record_bytes[54:58] = date_str.encode("shift_jis")

        # 7. 仕向銀行番号（4桁、右寄せゼロ埋め）
        sending_bank_code = "0000"  # TODO: 適切な値を設定
        record_bytes[58:62] = sending_bank_code.encode("shift_jis")

        # 8. 仕向銀行名（15バイト、左寄せスペース埋め、半角カナ）
        sending_bank_name = ""  # TODO: 適切な値を設定
        sending_bank_name_hankaku = cls._to_hankaku_kana(sending_bank_name)
        sending_bank_name_str = cls._pad_string(sending_bank_name_hankaku, 15, " ", "left")
        sending_bank_name_bytes = sending_bank_name_str.encode("shift_jis")
        record_bytes[62:77] = sending_bank_name_bytes[:15]

        # 9. 仕向支店番号（3桁、右寄せゼロ埋め）
        sending_branch_code = "000"  # TODO: 適切な値を設定
        record_bytes[77:80] = sending_branch_code.encode("shift_jis")

        # 10. 仕向支店名（15バイト、左寄せスペース埋め、半角カナ）
        sending_branch_name = ""  # TODO: 適切な値を設定
        sending_branch_name_hankaku = cls._to_hankaku_kana(sending_branch_name)
        sending_branch_name_str = cls._pad_string(sending_branch_name_hankaku, 15, " ", "left")
        sending_branch_name_bytes = sending_branch_name_str.encode("shift_jis")
        record_bytes[80:95] = sending_branch_name_bytes[:15]

        # 11. 預金種目: 1（普通）
        record_bytes[95] = ord("1")

        # 12. 口座番号（7桁、右寄せゼロ埋め）
        account_number = "0000000"  # TODO: 適切な値を設定
        record_bytes[96:103] = account_number.encode("shift_jis")

        # 13. ダミー（17桁、スペース）は既にスペースで埋められている

        # バイト配列を文字列に変換
        return record_bytes.decode("shift_jis")

    @classmethod
    def create_trailer_record(cls, record_count: int, total_amount: int) -> str:
        """
        トレーラー・レコードを作成（総合振込フォーマット準拠）

        Args:
            record_count: データレコード数
            total_amount: 合計金額

        Returns:
            トレーラーレコード（120バイト固定長）
        """
        # レコードをバイト配列として初期化（120バイト、スペースで埋める）
        record_bytes = bytearray(b" " * cls.RECORD_LENGTH)

        # 1. データ区分: 8（トレーラー）
        record_bytes[0] = ord("8")

        # 2. 合計件数（6桁、右寄せゼロ埋め）
        record_count_str = cls._pad_string(str(record_count), 6, "0", "right")
        record_bytes[1:7] = record_count_str.encode("shift_jis")

        # 3. 合計金額（12桁、右寄せゼロ埋め）
        total_amount_str = cls._pad_string(str(total_amount), 12, "0", "right")
        record_bytes[7:19] = total_amount_str.encode("shift_jis")

        # 4. ダミー（101桁、スペース）は既にスペースで埋められている

        # バイト配列を文字列に変換
        return record_bytes.decode("shift_jis")

    @classmethod
    def create_end_record(cls, record_count: int) -> str:
        """
        エンド・レコードを作成（総合振込フォーマット準拠）

        Args:
            record_count: 全レコード数（ヘッダー+データ+トレーラー）

        Returns:
            エンドレコード（120バイト固定長）
        """
        # レコードをバイト配列として初期化（120バイト、スペースで埋める）
        record_bytes = bytearray(b" " * cls.RECORD_LENGTH)

        # 1. データ区分: 9（エンド）
        record_bytes[0] = ord("9")

        # 2. ダミー（119桁、スペース）は既にスペースで埋められている

        # バイト配列を文字列に変換
        return record_bytes.decode("shift_jis")

    @classmethod
    def _normalize_column_names(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        列名を標準化（日本語→英語へのマッピング）

        Args:
            df: DataFrame

        Returns:
            列名を標準化したDataFrame
        """
        # 列名を標準化（空白を削除）
        df.columns = df.columns.str.strip()

        # 日本語列名から英語列名へのマッピング（総合振込フォーマット用）
        column_mapping = {
            # 被仕向銀行
            "金融機関コード": "bank_code",
            "金融機関名": "bank_name",  # 追加
            "銀行コード": "bank_code",
            "被仕向銀行コード": "bank_code",
            "銀行名": "bank_name",
            "被仕向銀行名": "bank_name",
            # 被仕向支店
            "支店コード": "branch_code",
            "被仕向支店コード": "branch_code",
            "支店名": "branch_name",  # 追加
            "被仕向支店名": "branch_name",
            # 口座情報
            "預金種目": "account_type",
            "口座種目": "account_type",
            "口座番号": "account_number",
            "口座名義（カナ）": "recipient_name",
            "口座名義(カナ)": "recipient_name",
            "受取人名": "recipient_name",
            # 金額
            "振込金額": "amount",
            "金額": "amount",
            # 顧客コード
            "顧客コード1": "customer_code1",
            "顧客コード2": "customer_code2",
            "顧客ID": "customer_code1",
            "顧客番号": "customer_code1",
            # その他
            "手形交換所番号": "clearing_house",
            "新規コード": "new_code",
        }

        # マッピングに従って列名を変換
        df = df.rename(columns=column_mapping)

        return df

    @classmethod
    def convert_excel_to_zengin(
        cls,
        excel_path: str,
        sheet_name: Optional[str] = None,
        requester_code: str = "",
        requester_name: str = "",
    ) -> List[str]:
        """
        Excelファイルを全銀フォーマットに変換

        Args:
            excel_path: Excelファイルのパス
            sheet_name: シート名（Noneの場合は最初のシート）
            requester_code: 依頼人コード
            requester_name: 依頼人名

        Returns:
            全銀フォーマットのレコードリスト

        Raises:
            ZenginFormatError: 変換エラー時
        """
        try:
            # Excelファイルを読み込む
            # sheet_nameがNoneの場合は最初のシートを読み込む
            if sheet_name is None:
                df = pd.read_excel(excel_path, sheet_name=0)
            else:
                df = pd.read_excel(excel_path, sheet_name=sheet_name)

            # dfが辞書の場合は最初のシートを使用（複数シート読み込みの場合）
            if isinstance(df, dict):
                if not df:
                    raise ZenginFormatError("Excelファイルにシートがありません")
                # 最初のシートを使用
                first_sheet_name = list(df.keys())[0]
                df = df[first_sheet_name]

            if df.empty:
                raise ZenginFormatError("Excelファイルが空です")

            # 列名を標準化（日本語→英語へのマッピング）
            df = cls._normalize_column_names(df)

            records = []
            total_amount = 0
            error_rows = []
            total_rows = len(df)

            import logging

            logger = logging.getLogger(__name__)
            logger.info(f"データ変換開始: 合計{total_rows}行を処理します")

            # 各行を処理
            for idx, row in df.iterrows():
                try:
                    # 進捗ログ（10行ごと、または最初の数行）
                    if idx < 5 or idx % 10 == 0:
                        logger.info(f"処理中: {idx + 1}/{total_rows}行目")

                    row_dict = row.to_dict()
                    record = cls.convert_row_to_record(row_dict, requester_code, requester_name)
                    records.append(record)

                    # 合計金額を計算
                    try:
                        amount_value = row_dict.get("amount", 0)
                        # 数値でない場合（文字列など）は変換を試みる
                        if pd.notna(amount_value):
                            amount = int(float(str(amount_value).replace(",", "")))
                            total_amount += amount
                    except (ValueError, TypeError):
                        # 金額計算エラーは警告のみ（処理は続行）
                        pass

                except ZenginFormatError as e:
                    error_rows.append(f"行 {idx + 2}: {str(e)}")  # +2はヘッダー行と0ベースインデックスのため
                    continue
                except Exception as e:
                    # 予期しないエラーも記録
                    error_rows.append(f"行 {idx + 2}: 予期しないエラー - {str(e)}")
                    continue

            if not records:
                raise ZenginFormatError("変換可能なデータがありません")

            if error_rows:
                raise ZenginFormatError(
                    "変換エラーが発生しました:\n" + "\n".join(error_rows[:10])
                )  # 最大10件まで表示

            # 全銀フォーマット（総合振込）のレコード構成
            # 1. ヘッダー・レコード（1レコード）
            # 2. データ・レコード（N レコード）
            # 3. トレーラー・レコード（1レコード）
            # 4. エンド・レコード（1レコード）

            result_records = []

            # 1. ヘッダーレコードを追加
            header = cls.create_header_record(len(records))
            result_records.append(header)

            # 2. データレコードを追加
            result_records.extend(records)

            # 3. トレーラーレコードを追加
            trailer = cls.create_trailer_record(len(records), total_amount)
            result_records.append(trailer)

            # 4. エンドレコードを追加
            end = cls.create_end_record(len(result_records))
            result_records.append(end)

            return result_records

        except FileNotFoundError:
            raise ZenginFormatError(f"ファイルが見つかりません: {excel_path}")
        except pd.errors.EmptyDataError:
            raise ZenginFormatError("Excelファイルが空です")
        except Exception as e:
            raise ZenginFormatError(f"ファイル読み込みエラー: {str(e)}")

    @staticmethod
    def save_zengin_file(
        records: List[str], output_dir: str, encoding: str = "shift_jis", newline: str = "\r\n"
    ) -> Tuple[str, str]:
        """
        全銀フォーマットデータをファイルに保存

        Args:
            records: 全銀フォーマットのレコードリスト（120バイト固定長）
            output_dir: 出力ディレクトリのパス
            encoding: エンコーディング（'utf-8' または 'shift_jis'）
            newline: 改行コード（'\n' または '\r\n'）

        Returns:
            (ファイルパス, ファイル名) のタプル

        Raises:
            ZenginFormatError: 保存エラー時
        """
        import os

        # 出力ディレクトリの存在確認と作成
        try:
            os.makedirs(output_dir, exist_ok=True)
        except OSError as e:
            raise ZenginFormatError(f"出力ディレクトリの作成に失敗しました: {str(e)}")

        # ファイル名を生成（タイムスタンプ付き）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"zengin_{timestamp}.txt"
        filepath = os.path.join(output_dir, filename)

        # レコードの検証（120バイト固定長チェック）
        for i, record in enumerate(records):
            # バイト数でチェック（Shift-JISエンコーディング）
            record_bytes = record.encode(encoding, errors="replace")
            byte_length = len(record_bytes)
            if byte_length != ZenginConverter.RECORD_LENGTH:
                raise ZenginFormatError(
                    f"レコード {i + 1} の長さが不正です: {byte_length}バイト "
                    f"(期待値: {ZenginConverter.RECORD_LENGTH}バイト)"
                )

        # ファイルに書き込み
        try:
            # エンコーディングと改行コードの設定
            if encoding == "shift_jis":
                # Shift-JISの場合
                with open(filepath, "w", encoding="shift_jis", newline="") as f:
                    for record in records:
                        f.write(record)
                        if newline == "\r\n":
                            f.write("\r\n")
                        elif newline == "\n":
                            f.write("\n")
                        else:
                            f.write(newline)
            else:
                # UTF-8の場合
                with open(filepath, "w", encoding="utf-8", newline="") as f:
                    for record in records:
                        f.write(record)
                        if newline == "\r\n":
                            f.write("\r\n")
                        elif newline == "\n":
                            f.write("\n")
                        else:
                            f.write(newline)

            return filepath, filename

        except UnicodeEncodeError as e:
            raise ZenginFormatError(f"文字エンコーディングエラー: {str(e)}")
        except IOError as e:
            raise ZenginFormatError(f"ファイル書き込みエラー: {str(e)}")
        except Exception as e:
            raise ZenginFormatError(f"予期しないエラー: {str(e)}")
