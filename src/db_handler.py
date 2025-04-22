import os
import sqlite3
import data_struct
from data_struct import Platform


class DBHandler:
    def __init__(self):
        def create_tables():
            self.cur.execute("""
                CREATE TABLE "tblPlatforms" (
                    "PlatformID"	INTEGER NOT NULL UNIQUE,
                    "PlatformName"	TEXT,
                    "IsEnabled"	INTEGER NOT NULL,
                    PRIMARY KEY("PlatformID")
                )
            """)

            self.cur.execute("""
                CREATE TABLE "tblFlatPlatFees" (
                    "PlatformID"	INTEGER NOT NULL UNIQUE,
                    "SharePlatFee"	REAL NOT NULL,
                    "SharePlatMaxFee"	REAL,
                    PRIMARY KEY("PlatformID"),
                    FOREIGN KEY("PlatformID") REFERENCES "tblPlatforms"("PlatformID")
                )
            """)

            self.cur.execute("""
                CREATE TABLE "tblFlatDealFees" (
                    "PlatformID"	INTEGER NOT NULL UNIQUE,
                    "FundDealFee"	REAL,
                    "ShareDealFee"	REAL NOT NULL,
                    "ShareDealReduceTrades"	REAL,
                    "ShareDealReduceAmount"	REAL,
                    PRIMARY KEY("PlatformID"),
                    FOREIGN KEY("PlatformID") REFERENCES "tblPlatforms"("PlatformID")
                )
            """)

            self.cur.execute("""
                CREATE TABLE "tblFundPlatFee" (
                    "PlatformID"	INTEGER NOT NULL,
                    "Band"	REAL NOT NULL,
                    "Fee"	REAL NOT NULL,
                    PRIMARY KEY("PlatformID","Band","Fee"),
                    FOREIGN KEY("PlatformID") REFERENCES "tblPlatforms"("PlatformID")
                )
            """)

            self.cur.execute("""
                CREATE TABLE "tblUserDetails" (
                    "UserID"	INTEGER NOT NULL UNIQUE,
                    "PensionValue"	REAL NOT NULL,
                    "SliderValue"	INTEGER NOT NULL,
                    "ShareTrades"	INTEGER NOT NULL,
                    "FundTrades"	INTEGER NOT NULL,
                    PRIMARY KEY("UserID")
                )
            """)

        if not os.path.exists("SIPPCompare.db"):
            db_exists = False
        else:
            db_exists = True

        self.conn = sqlite3.connect("SIPPCompare.db")
        self.cur = self.conn.cursor()
        if not db_exists:
            create_tables()

    def retrieve_plat_list(self) -> list:
        res = self.cur.execute("SELECT PlatformName FROM tblPlatforms").fetchall()
        plat_name_list = []
        for platform in res:
            plat_name_list.append(platform[0])

        return plat_name_list

    def retrieve_platforms(self) -> list[Platform]:
        platforms_res = self.cur.execute("""
            SELECT
            -- tblPlatforms
            tblPlatforms.PlatformID, PlatformName, IsEnabled,
            -- tblFlatPlatFees
            SharePlatFee, SharePlatMaxFee,
            -- tblFlatDealFees
            FundDealFee,
            ShareDealFee,
            ShareDealReduceTrades,
            ShareDealReduceAmount
            FROM tblPlatforms
            INNER JOIN tblFlatPlatFees ON
            tblPlatforms.PlatformID = tblFlatPlatFees.PlatformID
            INNER JOIN tblFlatDealFees ON
            tblPlatforms.PlatformID = tblFlatDealFees.PlatformID
        """).fetchall()

        platforms = []
        for platform in platforms_res:
            # plat_id, plat_name, enabled, share_plat_fee, share_plat_max_fee, fund_deal_fee,
            # share_deal_fee, share_deal_reduce_trades, share_deal_reduce_amount
            this_platform = [platform[0], platform[1], platform[2], platform[3], platform[4],
                             platform[5], platform[6], platform[7], platform[8]]
            platforms.append(this_platform)

        for platform in platforms:
            platform.insert(1, [[], []])

        fund_plat_fee_res = self.cur.execute("SELECT * FROM tblFundPlatFee").fetchall()
        for i in range(len(fund_plat_fee_res)):
            plat_id = fund_plat_fee_res[i][0]
            platforms[plat_id][1][0].append(fund_plat_fee_res[i][1])
            platforms[plat_id][1][1].append(fund_plat_fee_res[i][2])

        platform_obj_list: list[Platform] = []
        for platform in platforms:
            platform_obj_list.append(Platform(
                platform[0], platform[1], platform[2], platform[3],
                platform[6], platform[4], platform[5], platform[7],
                platform[8], platform[9]
            ))

        return platform_obj_list


    def write_user_details(self, pension_val: float, slider_val: int, share_trades: int, fund_trades: int):
        # Hardcode UserID as 0
        user_details_data = (0, pension_val, slider_val, share_trades, fund_trades)

        res = self.cur.execute("SELECT EXISTS(SELECT 1 FROM tblUserDetails)").fetchone()
        if res[0] == 0:
            self.cur.execute("INSERT INTO tblUserDetails VALUES (?, ?, ?, ?, ?)", user_details_data)
        else:
            self.cur.execute("""
                UPDATE tblUserDetails SET 
                UserID = ?,
                PensionValue = ?,
                SliderValue = ?,
                ShareTrades = ?,
                FundTrades = ?
            """, user_details_data)
        self.conn.commit()

    def retrieve_user_details(self) -> dict:
        res = self.cur.execute("SELECT EXISTS(SELECT 1 FROM tblUserDetails)").fetchone()
        if res[0] == 0:
            return {"NO_RECORD": None}

        res = self.cur.execute("SELECT * FROM tblUserDetails")
        res_tuple: tuple = res.fetchone()
        user_details_dict: dict[str, float | int] = {
            "user_id":      res_tuple[0],
            "pension_val":  res_tuple[1],
            "slider_val":   res_tuple[2],
            "share_trades": res_tuple[3],
            "fund_trades":  res_tuple[4]
        }

        return user_details_dict
