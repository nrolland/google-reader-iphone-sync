#import <UIKit/UIKit.h>
#import "browserViewController.h"

@interface Feeds2AppDelegate : NSObject {
    IBOutlet UIWindow *window;
	IBOutlet BrowserViewController * browseController;
}

@property (nonatomic, retain) UIWindow *window;

- (IBAction) showNavigation: (id) sender;
- (IBAction) showViewer: (id) sender;

@end
