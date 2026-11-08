/**
 * Method A (search by line)
 * 
 * Load and split the source file into a set of char arrays each of SOURCE_LINE_SIZE long
 * Load the pattern lines (each of fixed length SEARCH_LINE_SIZE)
 * 
 * Search the source lines looking for pattern, returning the first occurance of the pattern index
 * or -1 if not found
 * 
 * If the pattern is found in a line output to stdout:
 * **,PATTERN,line_number,index\n
 * 
 * 
 */

#include <stdio.h>
#include <omp.h>
#include "search.h" // include the search library

int main(int ac, char** av)
{
    // get the sourcefile and pattern file as parameters when run or error if not present
    char *sourcefile,*patternfile;

    if (ac<2)
    {
        FatalError("Usage command sourcefile.txt patternfile.txt");
    }

    sourcefile=av[1];
    patternfile=av[2];

    // load the source data into chunks of SOURCE_LINE_SIZE
    struct FileData fd;
    readSourceFile(sourcefile,&fd,FILE_LOAD_SPLIT_ONELINE,SOURCE_LINE_SIZE);

    // load the pattern file of fixed length lines
    struct FileData pat;
    readSourceFile(patternfile,&pat,FILE_LOAD_LINES,SEARCH_LINE_SIZE);

    // output some data
    printf("Read %ld lines for %ld characters in source, %ld lines for %ld chars in pattern\n",fd.lines,fd.length,pat.lines,pat.length);
    printf("Loaded patterns for searching are:\n");
    for (long p=0; p<pat.lines; ++p)
        printf("[%ld] %s\n",p,pat.data[p]);


    // loop through the patterns
    #pragma omp parallel for collapse(2) schedule(dynamic)
    for(long p=0; p<pat.lines; ++p)
    {
        // loop through the lines
        for(long l=0; l<fd.lines; ++l)
        {
            // do a search for the pattern on the line
            long s = Search(fd.data[l],fd.linesize,pat.data[p]
                ,pat.linesize,SEARCH_MODE_FIRST);
            // if found output the data format
            if (s>=0)
                printf("**,%s,%ld,%ld\n",pat.data[p],l,s);
        }
    }
    return 0;
}