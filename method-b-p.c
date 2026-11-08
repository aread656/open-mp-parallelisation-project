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
#define CHUNKSIZE 500
#include <string.h>
#include <stdio.h>
#include "search.h" // include the search library
#include <omp.h>

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
    for(long p=0; p<pat.lines; ++p)
    {
            int pattern_length = strlen(pat.data[p]);
            long pattern_count = 0;
            #pragma omp parallel for schedule(static)
            for (long chunk = 0; chunk < fd.length; chunk += CHUNKSIZE)
            {
                long l = CHUNKSIZE + pattern_length; //length to be searched through
                //upon reaching end of array, if the searching section crosses end of the array
                // (which is really very likely), bound l between current position and end of line
                if ((chunk+l) > fd.length) {l=fd.length - chunk;}
                long chunk_num = Search(fd.data[0]+chunk,l, pat.data[p],pat.linesize,SEARCH_MODE_COUNT);
                #pragma omp atomic
                pattern_count += chunk_num;
            }
            patterncount[p] = pattern_count;
    }

    //- Split the array into chunks of a given size
    //- Search through the chunk length + (pattern.length - 1)

    // now output the results
    for (long p=0; p<pat.lines; ++p)
        printf("**,%s,%ld\n",pat.data[p],patterncount[p]);

    
    return 0;
}