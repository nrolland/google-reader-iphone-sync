#import "tcHelpers.h"


@implementation tcHelpers
+ (BOOL) ensureDirectoryExists:(NSString *)path {
	NSFileManager *fileManager = [NSFileManager defaultManager];	
	if(![fileManager fileExistsAtPath: path]){
		[fileManager createDirectoryAtPath: path withIntermediateDirectories: YES attributes:nil error:nil];
	}
	if(![fileManager fileExistsAtPath: path]){
		NSLog(@"Directory couldn't be created: %@", path);
		return NO;
	}
	return YES;
}

@end
