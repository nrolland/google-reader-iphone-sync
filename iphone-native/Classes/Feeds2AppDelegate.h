#import <UIKit/UIKit.h>
#import "browserViewController.h"
#import "MainTabBarController.h"

@interface Feeds2AppDelegate : NSObject {
	IBOutlet UIWindow *window;
	IBOutlet id db;
	IBOutlet BrowserViewController * browseController;
	IBOutlet MainTabBarController * mainController;
	NSString * appDocsPath;
}

@property (nonatomic, retain) UIWindow *window;

- (IBAction) showNavigation: (id) sender;
- (IBAction) showViewer: (id) sender;

@end
