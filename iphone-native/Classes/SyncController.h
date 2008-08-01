#import <UIKit/UIKit.h>
#import <Foundation/Foundation.h>

@interface SyncController : UIViewController {
	IBOutlet id syncStatusView;
	IBOutlet id notSyncingView;
	
	IBOutlet id spinner;
	IBOutlet id downloadProgrssBar;
}
- (IBAction) sync: (id) sender;
- (IBAction) cancelSync: (id) sender;
@end
