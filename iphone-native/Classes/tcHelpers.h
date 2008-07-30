#define DEBUG

#ifdef DEBUG
	#define dbg NSLog
#else
	#define dbg( ... ) {}
#endif

@interface tcHelpers : NSObject {
}
+ (BOOL) ensureDirectoryExists:(NSString *)path;
+ (void) alertCalled: (NSString *) title saying: (NSString *) msg;
@end
