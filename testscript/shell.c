#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <error.h>

void main()
{
	char *parg[2];
	char buf[128];
	char *p;
	setvbuf(stdin, NULL, 2, 0);
	setvbuf(stdout, NULL, 2, 0);
	setvbuf(stderr, NULL, 2, 0);
	memset(buf, 0, sizeof(buf));	
	/* fgets(buf, sizeof(buf) - 1, stdin);
	
	p = strchr(buf, '\n');
	if(p) *p = 0;
	p = strchr(buf, '\r');
	if(p) *p = 0;
	printf("execute %s\n", buf);
	*/
	parg[0] = "/bin/sh";
	parg[1] = NULL;
	if(execve("/bin/sh", parg, NULL)	< 0)
	{
		perror("execve failed");
	}
}
