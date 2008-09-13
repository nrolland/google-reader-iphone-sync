#import "MainTabBarController.h"
#import "TCHelpers.h"

@implementation MainTabBarController
@synthesize navController;
- (void) activate {
	dbg(@"%@ activating", self);
	[[self itemList] redraw];
}

- (id) itemList {
	return [navController topViewController];
}

-(BOOL) itemListIsActive{
	return [self selectedIndex] == 0;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
	if(interfaceOrientation == UIInterfaceOrientationPortraitUpsideDown) return NO;
	return YES;
}

- (void) deactivate {
	dbg(@"%@ deactivating", self);
}
@end
