#import <UIKit/UIKit.h>


@interface MainTabBarController : UITabBarController {
	IBOutlet id statusView;
	IBOutlet id topLevelWindow;

}
- (void) activate;
- (void) deactivate;
@end
