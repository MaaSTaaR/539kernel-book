import os;
import re;
import subprocess;

htmlDir = 'book';

def getFullPath( filename ):
	return htmlDir + '/' + filename;

def rename():
	for currFilename in os.listdir( htmlDir ):
		if currFilename.endswith( '.html' ):
			os.rename( getFullPath( currFilename ), getFullPath( currFilename.replace( ' ', '_' ) ) );
		
def removeTexSetup( chapterText ):
	splittedText = chapterText.split( '<body>' );

	newHead = re.sub( r"(\s*)%texsetup%(\s|.)*%/texsetup%", '', splittedText[ 0 ], 0, re.MULTILINE );

	newText = newHead + '\n<body>' + splittedText[ 1 ];
	
	return newText;

def setTitle( chapterText, filename ):
	chapterTitle = filename.replace( '.html', '' ).replace( '_', ' ' );
	
	return chapterText.replace( '<title></title>', '<title>' + chapterTitle + '</title>' );

def formatChapterHead( chapterText ):
	matches = re.search( r"<h1 id=\"ch-(.*)\">(.*)Chapter(.*):(.*)</h1>", chapterText );
	
	if matches:
		originalHead = matches.group( 0 );
				
		headWithNoChapterWord = re.sub( r"Chapter(.*): ", '', originalHead, 1 );
		chapterId = re.search( r"<h1 id=\"ch-(.*)\">(.*)<span", headWithNoChapterWord ).group( 1 );

		formattedHead = headWithNoChapterWord.replace( '<h1 id="ch-' + chapterId + '">', '<h1 id="ch-"' + chapterId + '">Chapter ' ).replace( '</span>', '</span>.' );
				
		return chapterText.replace( originalHead, formattedHead );
		
	return chapterText;

# ... #

subprocess.call( [ 'sh', './generate_html.sh' ] );

rename();

for currFilename in os.listdir( htmlDir ):
		if currFilename.endswith( '.html' ):
			currFile = open( getFullPath( currFilename ), 'r' );
			chapterText = currFile.read();
			currFile.close();
			
			currFile = open( getFullPath( currFilename ), 'w' );
			finalHTML = formatChapterHead( setTitle( removeTexSetup( chapterText ), currFilename ) );
			currFile.write( finalHTML );
			currFile.close();
			
