import json
import sys
import csv
import os
import time
import logging
import shutil
import glob
from datetime import datetime
from wp.Wordpress import WordpressAPI
from cloverapi.cloverapi_client import CloverApiClient

startTime = datetime.now()
LogsToKeep = 100
BackUpsToKeep = 120

SyncFolder = "/var/www/vhosts/nagelsguns.net/httpdocs/cascadia/sync"
BackUpFolder = "/var/www/vhosts/nagelsguns.net/httpdocs/cascadia/backup"
LogFolder = "/var/www/vhosts/nagelsguns.net/httpdocs/cascadia/log"
LogFileName = LogFolder + "/" + datetime.now().strftime('inventory_%Y_%m_%d_%H_%M_%s.log')

def sorted_ls(path):
    mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
    return list(sorted(os.listdir(path), key=mtime))

logging.basicConfig(filename=LogFileName, filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)

WPAPI = WordpressAPI()

#Connect to clover client using api credentials
api_client = CloverApiClient(api_key='9765cced-d4d0-2c73-c0db-546e9eeb7175', merchant_id='Y92AAY3EZ4V81', api_url='https://api.clover.com')

CloverAccessoriesInventory = api_client.inventory_service.get_items_by_tag_id("SC0D3V4R926XR")

if( 'elements' in CloverAccessoriesInventory.keys() ):
    for Accessory in CloverAccessoriesInventory['elements']:
        if( 'stockCount' in Accessory.keys() and 'sku' in Accessory.keys() ):
            PostID = WPAPI.get_post_id_from_sku( Accessory['sku'] )
            if( PostID != 0 ):
                InventoryItem = api_client.inventory_service.get_item_stock_by_id( Accessory["id"] )
                WPAPI.update_post_meta( PostID, "_manage_stock", "yes")
                WPAPI.update_post_meta( PostID, "_stock", str( InventoryItem['stockCount'] ) )
                WPAPI.update_post_meta( PostID, "_stock_status", "instock" )
                logging.info('Updating Clover Item' + str( PostID ) )
            time.sleep(0.125)
        else:
            logging.info('Clover Stock Count NOT Found in SKU')
            print("Clover Stock Count NOT Found in SKU")

logging.info('---- Finished with Clover SKUs ----')
print( "---- Finished with Clover SKUs ----")

CSV_Filename = SyncFolder + "/products.csv"
CSV_New_Guns = {}
CSV_Used_Guns = {}

if( os.path.exists( CSV_Filename ) ):
    #parse the original csv file
    with open( CSV_Filename ) as CSVFile:
        reader = csv.DictReader( CSVFile )
        for row in reader:
            LogNumber = str( row['id'] )
            LogNumber = LogNumber.strip()
            LogNumber = LogNumber.replace("NGL-", "")
            SKU = str( row['sku'] )
            SKU = SKU.strip()
            if( row['used_firearm'] == "1" ):
                CSV_Used_Guns.update({ LogNumber : {"sku" : row['sku'], "quantity" : row['quantity'] } } )
            else:
                CSV_New_Guns.update({ SKU : {"quantity" : row['quantity'] } } )

    #check if the folder exists
    if( not os.path.exists( BackUpFolder ) ):
        os.mkdir( BackUpFolder )
    #make a backup copy of the file
    CurrentBackUpFileName = 'products from ' + str( datetime.now() ) + '.csv'
    SourceFile = SyncFolder + '/products.csv'
    DestinationFile = BackUpFolder + "/" + CurrentBackUpFileName
    shutil.copy( SourceFile, DestinationFile )
    os.remove( SourceFile )
else:
    logging.info('Cannot find inventory file, Exiting...')
    print("Cannot find inventory file, Exiting...")
    sys.exit()


logging.info('---- Finished parsing csv file ----')
print( "---- Finished parsing CSV file ----")

#parse the new guns
if( len( CSV_New_Guns ) != 0 ):
    for SKU in CSV_New_Guns:
        if( not SKU == "" ):
            PostID = WPAPI.get_post_id_from_sku( SKU )
            if( PostID != 0 ):
                WPAPI.update_post_meta( PostID, "_manage_stock", "yes")
                WPAPI.update_post_meta( PostID, "_stock", CSV_New_Guns[ SKU ]['quantity'] )
                WPAPI.update_post_meta( PostID, "_stock_status", "instock" )
                WPAPI.update_post_status( PostID, "publish" )
                logging.info( "New Gun:" + SKU + " is being updated-POST-" + str( PostID ) )
                print( "New Gun:" + SKU + " is being updated-POST-" + str( PostID ) )
        else:
            logging.info( "New Gun SKU is empty -- Skipping" )
            print( "New Gun SKU is empty -- Skipping" )
else:
    logging.info( 'the new gun dict is empty' )
    print("the new gun dict is empty")

logging.info( "---- Finished with new guns ----" )
print( "---- Finished with new guns ----")

#parse the used guns
#if( len( CSV_Used_Guns ) != 0 ):
    #get ALL inventory that needs to be purged
    #logging.info( "---- Purging UsedGun Inventory ----" )
    #print( "---- Purging UsedGun Inventory ----")
    #UsedGunPurgeableInventoryItems = WPAPI.get_purgeable_inventory_items( "product", "private")
    #if( len( UsedGunPurgeableInventoryItems ) > 0 ):
        #delete all the purgeable inventory items
        #for ItemNumber in UsedGunPurgeableInventoryItems:
            #logging.info( "Purging: " + ItemNumber + " From Inventory" )
            #print( "Purging: " + ItemNumber + " From Inventory")
            #WPAPI.delete_post( UsedGunPurgeableInventoryItems[ItemNumber] )
    #logging.info( "---- Starting Used Guns Inventory ----" )
    #print( "---- Starting Used_Guns Inventory ----")
    #get active used gun inventory items
    #UsedGunInventoryItems = WPAPI.get_inventory_items( "product", "publish", "13291")
    #print( str( type( UsedGunInventoryItems ) ) )
    #print( str( UsedGunInventoryItems ) )
    #print( str( UsedGunInventoryItems['174746'] ) )

    #sys.exit()
    #UsedGunInventoryItems has no NGL prefix on keys
    #if( type( UsedGunInventoryItems ) is dict ):
        #for CSVUsedGunItemNumber in CSV_Used_Guns:
            #str( CSVUsedGunItemNumber )
            #CSVUsedGunItemNumber = CSVUsedGunItemNumber.replace("NGL-","")
            #CSVUsedGunItemNumber = CSVUsedGunItemNumber.strip()

            #if( not CSVUsedGunItemNumber == "" ):
                #check if the current item number exists in the current inventory
                #if( CSVUsedGunItemNumber in UsedGunInventoryItems.keys() ):
                    #logging.info( CSVUsedGunItemNumber + " is being updated" )
                    #print( CSVUsedGunItemNumber + " is being updated")
                    #UsedGun = UsedGunInventoryItems[CSVUsedGunItemNumber]
                    #Set Stock Quantity if necessary
                    #WPAPI.update_post_meta( UsedGun['PostID'], "_stock", str( CSV_Used_Guns[CSVUsedGunItemNumber]['quantity'] ) )
                    #Set Stock StockStatus if necessary
                    #WPAPI.update_post_meta( UsedGun['PostID'], "_stock_status", "instock" )
                    #Set ManageStock if necessary
                    #WPAPI.update_post_meta( UsedGun['PostID'], "_manage_stock", "yes" )
                    #Set Post Modified Date
                    #WPAPI.update_post_modified_datetime( UsedGun['PostID'] )
                    #remove from dict
                    #del UsedGunInventoryItems[ CSVUsedGunItemNumber ]
            #else:
                #logging.info( "Usedgun has an empty item number and is being skipped" )
                #print( "UsedGun has an empty item number and is being skipped" )

        #Mark all remaining items are purgeable because they were not matched
        #for PurgeableItemNumber in UsedGunInventoryItems:
            #if( not PurgeableItemNumber == "" ):
                #logging.info( "Marking:" + PurgeableItemNumber + " as purgeable inventory" )
                #print( "Marking:" + PurgeableItemNumber + " as purgeable inventory" )
                #PurgeableUsedGun = UsedGunInventoryItems[PurgeableItemNumber]
                #Set Stock Quantity to zero
                #WPAPI.update_post_meta( PurgeableUsedGun['PostID'], "_stock", str( 0 ) )
                #Set StockStatus to outofstock
                #WPAPI.update_post_meta( PurgeableUsedGun['PostID'], "_stock_status", "outofstock" )
                #Set Post Status
                #WPAPI.update_post_status( PurgeableUsedGun['PostID'], "private" )
                #Set Post Modified Date
                #WPAPI.update_post_modified_datetime( PurgeableUsedGun['PostID'] )
            #else:
                #logging.info( "Purgeable Item number [used gun] was blank and therefore skipped" )
                #print( "Purgeable Item Number [used gun] was blank and therefore skipped" )
#else:
    #logging.info( "the new gun dict is empty" )
    #print("the new gun dict is empty")

BackUpFiles = sorted_ls( BackUpFolder )
BackUpFilesCount = len( BackUpFiles )
if( BackUpFilesCount > BackUpsToKeep ):
    BackUpDeleteCount = BackUpFilesCount - BackUpsToKeep
    for x in range( BackUpDeleteCount ):
        BackUpFileToDelete = BackUpFiles.pop(0)
        logging.info('Removing Backup CSV:' + BackUpFileToDelete)
        os.remove( BackUpFolder + "/" + BackUpFileToDelete )

LogFiles = sorted_ls( LogFolder )
LogFilesCount = len( LogFiles )
if( LogFilesCount > LogsToKeep ):
    LogFileDeleteCount = LogFilesCount - LogsToKeep
    for x in range( LogFileDeleteCount ):
        LogFileToDelete = LogFiles.pop(0)
        logging.info('Removing Log File:' + LogFileToDelete)
        os.remove( LogFolder + "/" + LogFileToDelete )

logging.info( "Completed Inventory Sync" )
logging.info( "Elapsed Time:" + str( datetime.now() - startTime) )
print("Completed Inventory Sync")
print("Elapsed Time:" + str( datetime.now() - startTime) )