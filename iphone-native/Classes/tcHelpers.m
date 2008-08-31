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

+ (void) debugAlertCalled: (NSString *) title saying: (NSString *) msg {
	#ifdef DEBUG
	[self alertCalled: title saying: msg];
	#endif
}

+ (void) alertCalled: (NSString *) title saying: (NSString *) msg {
	[[[[UIAlertView alloc]
		initWithTitle:title message: msg delegate:nil cancelButtonTitle:nil otherButtonTitles:@"OK", nil]
			autorelease] show];
}

+ (NSUInteger) lastIndexInPath: (NSIndexPath *) indexPath {
	return [indexPath indexAtPosition: [indexPath length] - 1];
}

@end
