#import <UIKit/UIKit.h>
#import <Foundation/Foundation.h>
#import "BackgroundShell.h"

@interface SyncController : UIViewController {
	IBOutlet id syncStatusView;
	IBOutlet id notSyncingView;
	IBOutlet id cancelButton;
	IBOutlet id okButton;
	IBOutlet id spinner;
	IBOutlet id feedList;
	IBOutlet id appSettings;
	
	BackgroundShell * syncThread;
	BOOL syncRunning;
	IBOutlet id window;
	
	IBOutlet id itemsController;
	IBOutlet id db;
	
	IBOutlet id status_currentTask;
	IBOutlet id status_taskProgress;
	IBOutlet id status_mainProgress;
	
	int totalTasks;
	int totalStepsInCurrentTask;
	NSString * last_output_line;
}
- (IBAction) sync: (id) sender;
- (IBAction) syncFeedListOnly: (id) sender;
- (IBAction) cancelSync: (id) sender;
- (IBAction) hideSyncView: (id)sender;
@end
