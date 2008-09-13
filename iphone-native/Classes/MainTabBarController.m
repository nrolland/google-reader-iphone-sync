#import "MainTabBarController.h"
#import "TCHelpers.h"

@implementation MainTabBarController
@synthesize navController;
- (void) activate {
	dbg(@"%@ activating", self);
	[topLevelWindow addSubview:[self view]];
	// TODO: stop being underneath the statusbar. it does this for us when the screen rotates, so we much be able to do it somehow...
	// this is a hacky version that only works if it's in portrait mode:
	[[self view] setCenter: CGPointMake(160,250)];
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
	if([self itemListIsActive]) {
		return YES;
	}
	return interfaceOrientation == UIInterfaceOrientationPortrait;
}

- (void) deactivate {
	dbg(@"%@ deactivating", self);
	[[self view] removeFromSuperview];
}
@end
