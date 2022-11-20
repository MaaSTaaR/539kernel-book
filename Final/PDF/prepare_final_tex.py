import os;
import re;
import subprocess;

texDir = 'generated_tex';

def getFullPath( filename ):
	return texDir + '/' + filename;

def breakLongListInline( chapterText ):
	return chapterText.replace( 'lstinline!print_character_S_with_BIOS!', 'texttt{print\_character\_S\_with\_BIOS}' ).replace( 'lstinline!wait_drive_until_ready!', 'texttt{wait\_drive\_until\_ready}' ).replace( 'lstinline!FILENAME_LENGTH!', 'texttt{FILENAME\_LENGTH}' ).replace( 'lstinline!tell_pic_master_where_pic_slave_is_connected!', 'texttt{tell\_pic\_master\_where\_pic\_slave\_is\_connected}' );
	
# ... #

print( 'Generating Tex Files' );

for currFilename in os.listdir( texDir ):
		if currFilename.endswith( '.tex' ):
			print( 'Processing ' + currFilename );
			
			currFile = open( getFullPath( currFilename ), 'r' );
			chapterText = currFile.read();
			currFile.close();
			
			finalTex = breakLongListInline( chapterText );
			
			currFile = open( getFullPath( currFilename ), 'w' );
			currFile.write( finalTex );
			currFile.close();
			
