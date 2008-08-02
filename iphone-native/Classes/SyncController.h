#import <UIKit/UIKit.h>
#import <Foundation/Foundation.h>

@interface SyncController : UIViewController {
	IBOutlet id syncStatusView;
	IBOutlet id notSyncingView;
       IBOutlet id cancelButton;
       IBOutlet id okButton;
	IBOutlet id spinner;
	IBOutlet id downloadProgrssBar;
       NSThread * syncThread;
       IBOutlet id runningOutput;
       BOOL syncRunning;
}
- (IBAction) sync: (id) sender;
- (IBAction) cancelSync: (id) sender;
@end
