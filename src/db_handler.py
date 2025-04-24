import os
import sqlite3

import resource_finder
from data_struct import Platform


class DBHandler:
    def __init__(self):
        # Function to create all necessary database tables if the DB file doesn't exist
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

        if not os.path.exists(resource_finder.get_res_path("SIPPCompare.db")):
            db_exists = False
        else:
            db_exists = True

        self.conn = sqlite3.connect(resource_finder.get_res_path("SIPPCompare.db"))
        self.cur = self.conn.cursor()
        if not db_exists:
            create_tables()

    # Retrieve the list of platform names for list population
    def retrieve_plat_list(self) -> list:
        res = self.cur.execute("SELECT PlatformName FROM tblPlatforms").fetchall()
        plat_name_list = []
        for platform in res:
            plat_name_list.append(platform[0])

        return plat_name_list

    def write_platforms(self, plat_list: list[Platform]):
        for i in range(len(plat_list)):
            platforms_data = [
                plat_list[i].plat_id,
                plat_list[i].plat_name,
                plat_list[i].enabled
            ]

            flat_plat_fees_data = [
                plat_list[i].plat_id,
                plat_list[i].share_plat_fee,
                plat_list[i].share_plat_max_fee
            ]

            flat_deal_fees_data = [
                plat_list[i].plat_id,
                plat_list[i].fund_deal_fee,
                plat_list[i].share_deal_fee,
                plat_list[i].share_deal_reduce_trades,
                plat_list[i].share_deal_reduce_amount
            ]

            res = self.cur.execute(f"""
            SELECT EXISTS(
                SELECT PlatformID FROM tblPlatforms
                WHERE PlatformID = {i}
            )""").fetchall()

            if res[0][0] == 1:
                self.cur.execute(f"""
                    UPDATE tblPlatforms SET 
                    PlatformID = ?,
                    PlatformName = ?,
                    IsEnabled = ?
                    WHERE PlatformID = {i}
                """, platforms_data)

                self.cur.execute(f"""
                    UPDATE tblFlatPlatFees SET 
                    PlatformID = ?,
                    SharePlatFee = ?,
                    SharePlatMaxFee = ?
                    WHERE PlatformID = {i}
                """, flat_plat_fees_data)

                self.cur.execute(f"""
                    UPDATE tblFlatDealFees SET
                    PlatformID = ?,
                    FundDealFee = ?,
                    ShareDealFee = ?,
                    ShareDealReduceTrades = ?,
                    ShareDealReduceAmount = ?
                    WHERE PlatformID = {i}
                """, flat_deal_fees_data)

                self.cur.execute(f"DELETE FROM tblFundPlatFee WHERE PlatformID = {i}")
            else:
                self.cur.execute("INSERT INTO tblPlatforms VALUES (?, ?, ?)", platforms_data)
                self.cur.execute("INSERT INTO tblFlatPlatFees VALUES (?, ?, ?)", flat_plat_fees_data)
                self.cur.execute("INSERT INTO tblFlatDealFees VALUES (?, ?, ?, ?, ?)", flat_deal_fees_data)

            exec_str = f"INSERT INTO tblFundPlatFee VALUES\n"
            for x in range(len(plat_list[i].fund_plat_fee[0])):
                band = plat_list[i].fund_plat_fee[0][x]
                fee = plat_list[i].fund_plat_fee[1][x]
                exec_str += f"({i}, {band}, {fee}),\n"
            exec_str = exec_str[:-2]
            self.cur.execute(exec_str)

            self.conn.commit()

    # Retrieve all info about all platforms in DB and initialise Platform objects
    def retrieve_platforms(self) -> list[Platform]:
        # Retrieve all one-to-one relations
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

        # Insert 2D array into each platform data in preparation for fund_plat_fee retrival
        for platform in platforms:
            platform.insert(1, [[], []])

        # Get all records from tblFundPlatFee, add them to the platforms list based on ID
        # WARNING: This code is dependent on PlatformID being sequential from 0 in DB records
        fund_plat_fee_res = self.cur.execute("SELECT * FROM tblFundPlatFee ORDER BY PlatformID ASC").fetchall()
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

    # This function writes the details the user entered this session to the DB
    def write_user_details(self, pension_val: float, slider_val: int, share_trades: int, fund_trades: int):
        # Hardcode UserID as 0
        user_details_data = (0, pension_val, slider_val, share_trades, fund_trades)

        # Check if there is already a record in tblUserDetails
        res = self.cur.execute("SELECT EXISTS(SELECT 1 FROM tblUserDetails)").fetchone()
        if res[0] == 0:
            # If there isn't then insert a new record
            self.cur.execute("INSERT INTO tblUserDetails VALUES (?, ?, ?, ?, ?)", user_details_data)
        else:
            # If there is then update the existing record (only ever one record as of now)
            self.cur.execute("""
                UPDATE tblUserDetails SET 
                UserID = ?,
                PensionValue = ?,
                SliderValue = ?,
                ShareTrades = ?,
                FundTrades = ?
            """, user_details_data)
        self.conn.commit()

    # Function to retrieve details entered by the user in prev session from DB
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
