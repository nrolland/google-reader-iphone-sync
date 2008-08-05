#import <UIKit/UIKit.h>
#import <Foundation/Foundation.h>
#import "BackgroundShell.h"

@interface SyncController : UIViewController {
	IBOutlet id syncStatusView;
	IBOutlet id notSyncingView;
	IBOutlet id cancelButton;
	IBOutlet id okButton;
	IBOutlet id spinner;
	IBOutlet id downloadProgrssBar;
	BackgroundShell * syncThread;
	IBOutlet id runningOutput;
	BOOL syncRunning;
	IBOutlet id window;
}
- (IBAction) sync: (id) sender;
- (IBAction) cancelSync: (id) sender;
- (IBAction) hideSyncView: (id)sender;
@end
