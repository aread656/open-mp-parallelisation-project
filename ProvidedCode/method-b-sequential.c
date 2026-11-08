/**
 * Method B (search single block)
 * 
 * Load the source file into a single char array (one line)
 * Load the pattern lines (each of fixed length SEARCH_LINE_SIZE)
 * 
 * Search the source line looking for patterns, returning the number 
 * of instances of the pattern found (0 if not found)
 * 
 * For each pattern output a line to stdout of the format:
 * **,pattern,count\n
 * 
 * 
 */

#include <stdio.h>
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
    readSourceFile(sourcefile,&fd,FILE_LOAD_ONELINE,1);

    // load the pattern file of fixed length lines
    struct FileData pat;
    readSourceFile(patternfile,&pat,FILE_LOAD_LINES,SEARCH_LINE_SIZE);

    // output some data
    printf("Read %ld lines for %ld characters in source, %ld lines for %ld chars in pattern\n",fd.lines,fd.length,pat.lines,pat.length);
    printf("Loaded patterns for searching are:\n");
    for (long p=0; p<pat.lines; ++p)
        printf("[%ld] %s\n",p,pat.data[p]);


    // array for the results of the pattern counting, initialise to zero
    long patterncount[pat.lines];
    for(long i=0; i<pat.lines; ++i)
    {
        patterncount[i]=0;
    }

    // loop through the patterns
    #pragma omp parallel for schedule(static)
    for(long p=0; p<pat.lines; ++p)
    {
            // do a search for the pattern on the line using counter mode, incrementing the pattern counter
            // we only have one line in this mode fd.data[0]
            patterncount[p] += Search(fd.data[0],fd.linesize,pat.data[p],pat.linesize,SEARCH_MODE_COUNT);
    }

    // now output the results
    for (long p=0; p<pat.lines; ++p)
        printf("**,%s,%ld\n",pat.data[p],patterncount[p]);

    
    return 0;
}