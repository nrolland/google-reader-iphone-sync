#import "MainTabBarController.h"
#import "TCHelpers.h"

@implementation MainTabBarController
@synthesize navController;
- (void) activate {
	dbg(@"%@ activating", self);
	isActive = YES;
	[self setListScrollToTop:YES];
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

- (void) didRotateFromInterfaceOrientation:(UIInterfaceOrientation)previousOrientation {
	[[self tabBar] setHidden: !isActive];
}

- (void) setListScrollToTop:(BOOL) doScroll {
	dbg(@"scrolling list view to top? %s -- %@", doScroll ? "YES" : "NO", [[navController topViewController] listView]);
	[[[navController topViewController] listView] setScrollsToTop:doScroll];
}

- (void) deactivate {
	dbg(@"%@ deactivating", self);
	[self setListScrollToTop:NO];
	isActive = NO;
}
@end
