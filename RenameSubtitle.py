import os
import sys
import logging
import fnmatch
from pathlib import Path
import re
import datetime
import exifread
from pymediainfo import MediaInfo


#For C:\\111\\222\\333.444
#DirName = C:\\111\\222\\
#FileName = 333.444
#BaseName = 333
#ExtName = .444

gSeqNum = re.compile( ".*?([0-9]{2,})[ -_].*" , re.IGNORECASE )
def TryRenameFile( aSubtitlePath , aPossibleVideoPath ):
    seqNum = None
    aryMatch = gSeqNum.match(aSubtitlePath.stem)
    if aryMatch != None and len(aryMatch.groups()) == 1:
        seqNum = aryMatch.group(1)

    matchedVideo = None
    for videoPath in aPossibleVideoPath:
        if aSubtitlePath.stem == videoPath.stem:
            matchedVideo = videoPath
            logging.info( "Same name for {}".format(aSubtitlePath.stem) )
            break
        if seqNum != None and seqNum in videoPath.stem:
            matchedVideo = videoPath
            logging.info( "SeqNum {} match for {}".format(seqNum, aSubtitlePath.stem) )
            break

    if videoPath != None:
        newPath = aSubtitlePath.parent / (matchedVideo.stem + aSubtitlePath.suffix)
        logging.info( "{} => {}".format(aSubtitlePath.stem , newPath.stem) )
        os.rename( aSubtitlePath , newPath )
    else:
        logging.warning( "Cannot find matched video for {}".format(aSubtitlePath.stem) )




if __name__ == "__main__" :
    strScriptDir = os.path.dirname( os.path.realpath(__file__) )
    strLogDir = "{}\\Logs".format( strScriptDir )
    if not os.path.isdir( strLogDir ) :
        os.makedirs( strLogDir )

    strPath = os.path.realpath( os.getcwd() )
    if ( 2 <= len(sys.argv) ) :
        strPath = os.path.realpath( sys.argv[1] )

    logger = logging.getLogger()
    logger.setLevel( logging.INFO )

    fmtConsole = logging.Formatter( "[%(asctime)s][%(levelname)s]: %(message)s" )
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter( fmtConsole )
    logger.addHandler( consoleHandler )

    fmtFile = logging.Formatter( "[%(asctime)s][%(levelname)s][%(process)04X:%(thread)04X][%(filename)s][%(funcName)s_%(lineno)d]: %(message)s" )
    fileHandler = logging.FileHandler( "{}\\{}-{}.txt".format(strLogDir , os.path.basename(strPath) , datetime.datetime.now().strftime("%Y%m%d_%H%M%S")), encoding="utf8" )
    fileHandler.setFormatter( fmtFile )
    logger.addHandler( fileHandler )



    reVideo = re.compile( ".*\.(mp4|mkv|mov|avi)$" , re.IGNORECASE )
    reSub = re.compile( ".*\.(txt|sub|ass|ssa)$" , re.IGNORECASE )
    try :
        logging.info( "Search {} under \"{}\"".format(reSub,strPath) )
        aryVideo = []
        arySub = []
        if ( os.path.isdir(strPath) ) :
            for strDir , lsDirNames , lsFileNames in os.walk( strPath ) :
                for strFileName in lsFileNames :
                    if reVideo.match( strFileName ) :
                        strPath = os.path.join( strDir , strFileName )
                        aryVideo.append( Path(strPath) )
                    elif reSub.match( strFileName ) :
                        strPath = os.path.join( strDir , strFileName )
                        arySub.append( Path(strPath) )

            for sub in arySub:
                TryRenameFile( sub , aryVideo )
        else :
            logging.info( "Usage: {} <directory path>".format( os.path.basename(__file__) ) )
    except Exception as ex :
        logging.exception( "strPath={}".format(strPath) )

    logging.info( "End of the program" )
    logging.shutdown()
    print( "Press any key to leave" )
    input()