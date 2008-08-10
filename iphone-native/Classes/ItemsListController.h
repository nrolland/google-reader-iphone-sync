#import <UIKit/UIKit.h>
#import <Foundation/Foundation.h>

@interface ItemsListController : UIViewController {
	IBOutlet id dataSource;
	IBOutlet id listView;
	
	IBOutlet id optionsView;
	BOOL optionsAreVisible;
	IBOutlet id showHideOptionsButton;
}
- (IBAction) toggleOptions:(id)sender;
-(IBAction) refresh: (id) sender;
@end
