#import "tcDirList.h"


@implementation tcDirList
- (id) init {
	return [self initWithPath: @"/"];
}
	
- (id) initWithPath: (NSString *) initPath {
	self = [super init];
	path = initPath;
	return self;
}

- (NSString *) path{
	return path;
}

- (NSString *)firstFile{
	NSString *first = [self fileNextTo:nil before:NO];
	NSLog(@"first is %@", first);
	return first;
}

- (NSString *)fileBefore:(NSString*) current {
	NSString *prev = [self fileNextTo:current before:YES];
	NSLog(@"prev is %@", prev);
	return prev;
}

- (NSString *)fileAfter:(NSString*) current {
	NSString *next = [self fileNextTo:current before:NO];
	NSLog(@"next is %@", next);
	return next;
}

- (NSString *)fileNextTo:(NSString*) current before:(BOOL) getBeforeFile {
	NSDirectoryEnumerator *direnum = [[NSFileManager defaultManager]
									  enumeratorAtPath:path];
	NSString *pname;
	NSString *lastFilename = nil;

	while (pname = [direnum nextObject])
	{
		[direnum skipDescendents]; // why must i call this every loop iteration? o_O
		if(current == nil){
			// get the first item
			return pname;
		}
			
		if ([pname isEqualToString:current])
		{
			if(getBeforeFile){
				return lastFilename;
			} else {
				return [direnum nextObject];
			}
		}
		lastFilename = pname;
	}
	return nil;
}

- (void) dealloc {
	[path release];
	[super dealloc];
}
@end
