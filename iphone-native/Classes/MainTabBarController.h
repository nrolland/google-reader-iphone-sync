#import <UIKit/UIKit.h>


@interface MainTabBarController : UITabBarController {
	IBOutlet id statusView;
	IBOutlet id topLevelWindow;
	IBOutlet id itemList;
}
@property(readonly) id itemList;
- (void) activate;
- (void) deactivate;
@end
