#import <UIKit/UIKit.h>
#import "TCObjectExtensions.h"


@implementation NSObject (TCObjectExtensions)

- (id) globalApp { return [UIApplication sharedApplication]; }
- (id) globalAppDelegate { return [[UIApplication sharedApplication] delegate]; }
- (id) globalAppSettings { return [[[UIApplication sharedApplication] delegate] settings]; }

@end

