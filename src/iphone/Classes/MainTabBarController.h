#import <UIKit/UIKit.h>


@interface MainTabBarController : UITabBarController {
	IBOutlet id statusView;
	IBOutlet id topLevelWindow;
	IBOutlet id navController;
	BOOL isActive;
}
@property(readonly) id navController;
- (void) activate;
- (void) deactivate;
@end
