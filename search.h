// Search Library for CSC4010 Assignment 1
// David Cutting
//
// Note: you are required to use this unmodified (you can add debug or even change things)
// BUT for assessment execution an original copy of this library will be used!
//
// Yes the search is slow and inefficient but this is deliberate I tell you.
//

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define SOURCE_LINE_SIZE 1024       // default splitting size when we wish to split the source file
#define SEARCH_LINE_SIZE 6          // default line size for the search (pattern) file

// Modes for loading file
#define FILE_LOAD_SPLIT_ONELINE 1   // Load a one-line file and split into chunks
#define FILE_LOAD_ONELINE 2         // Just load the file as a single line (array)
#define FILE_LOAD_LINES 3           // Load a file that is already in lines of fixed length

// Modes for searching
#define SEARCH_MODE_FIRST 1         // Just return the location of the first needle in the hackstack (or -1 if not found)
#define SEARCH_MODE_COUNT 2         // Return a count of the number of needles in the haystack (0 if none found)

// Send an error string to stderr and quit with a non-0 code
void FatalError(const char *err)
{
    fprintf(stderr,"%s\n",err);
    exit(1);
}

// Struct to hold loaded file data
struct FileData {
    long length;
    long lines;
    long linesize;
    char **data;
};

// Read a source file parameters:
// filename - filename/path to load
// fd - pointer to a FileData struct to put the data into
// MODE - FILE_LOAD_ mode
// linesize - if splitting or loading fixed length lines the size, otherwise not used
void readSourceFile(const char *filename, struct FileData *fd, int MODE, long linesize)
{
    FILE *fp = fopen(filename,"r");             // open the file
    if (!fp) FatalError("Cannot open file");    // fatal error if cannot open

    // now size up the file
    fseek(fp,0,SEEK_END);           // go to the end
    fd->length = ftell(fp);         // get the current position (length of file)
    if (MODE == FILE_LOAD_ONELINE)  // if we're loading one line this is the line length and num of lines is 1
    {
        fd->linesize = fd->length;
        linesize = fd->linesize;
        fd->lines = 1;
    }
    else                            // otherwise lines is size/linesize
    {
        fd->linesize = linesize;
        fd->lines = fd->length/(linesize+1);
    }
    fseek(fp,0,SEEK_SET);       // back to the start of the file to load data
    

    fd->data = (char**)malloc(fd->lines * sizeof(char**));    // allocate memory for the pointers to lines
    if(fd->data == NULL)
    {
        FatalError("Cannot allocate memory");
    }

    for(long i=0; i<fd->lines; ++i)     // loop through the lines
    {
        fd->data[i] = (char*)malloc(fd->linesize); // allocate memory for the line
        if (fd->data[i] == NULL)
        {
            FatalError("Cannot allocate memory");
        }
        
        fread(fd->data[i], fd->linesize, 1, fp);    // read the line into the memory
    
        if (MODE == FILE_LOAD_LINES)            // if we're doing fixed-length lines skip the newline char
        {
            char ret;
            fread(&ret, 1, 1, fp);
        }
    }

    fclose(fp);
}

// Do a very simple (and inefficient!) search
// haystack - char array to search in
// haylen - length of the haystack to search
// needle - pattern to search haystack for
// nedlen - length of the needle/pattern
// SEARCHMODE - SEARCH_MODE_ setting
long Search(const char *haystack, const long haylen, const char *needle, const long nedlen, int SEARCHMODE)
{
   long count = 0; // counter if we need it
   
    // outer loop goes along the haystack (to haystack length-needle length)
    for(long outer=0; outer<(haylen-nedlen); ++outer)
    {
        //printf("%ld ",outer);
        // inner loop now checks for the needle
        for(long inner=0; inner<nedlen; ++inner)
        {
            // if the char in haystack doesn't match the char in needle then break the inner loop
            if(haystack[outer+inner]!=needle[inner]) break;
            // if it does match and we're now at the end of needle then all needle chars must have matched (a match!)
            if(inner == nedlen-1)
            {
                // if we're looking for the first hit then just return (from Search) the location outer is at (start of needle)
                if (SEARCHMODE == SEARCH_MODE_FIRST)
                    return outer;
                else // otherwise increment the count and skip the outer loop to the end of needle
                {   
                    ++count;        // increment the count
                    outer+=inner;   // skip the outer loop past the found word
                }
            }
        }
    }

    if (SEARCHMODE == SEARCH_MODE_FIRST)
        return -1;     // in first mode getting here means no match so return -1
    return count;   // otherwise we're counting so return the count
}
