#import <UIKit/UIKit.h>
#import "BrowserViewController.h"
#import "MainTabBarController.h"

@interface GRiSAppDelegate : NSObject {
	IBOutlet UIWindow *window;
	IBOutlet id db;
	IBOutlet BrowserViewController * browseController;
	IBOutlet MainTabBarController * mainController;
	IBOutlet id appSettings;
	IBOutlet id itemListDelegate;
	IBOutlet id feedList;
	IBOutlet id syncController;

	IBOutlet id optionsView;
	IBOutlet id optionsUnderlayView;
	BOOL inItemViewMode;
	BOOL loading;
}

@property (nonatomic, retain) UIWindow *window;

- (IBAction) toggleOptions: (id) sender;
- (IBAction) showNavigation: (id) sender;
- (IBAction) showViewer: (id) sender;
- (NSString *) appDocsPath;
- (id) settings;
- (IBAction) markItemsAsRead: (id) sender;
- (IBAction) markItemsAsUnread: (id) sender;
@end
