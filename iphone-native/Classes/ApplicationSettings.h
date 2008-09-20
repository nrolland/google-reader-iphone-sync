#import <UIKit/UIKit.h>
#import <Foundation/Foundation.h>

@interface ApplicationSettings : NSObject {
	NSString * docsPath;
	NSMutableDictionary * plistData;
	NSString * plistName;
	
	NSArray * possibleTags;
	
	IBOutlet id emailField;
	IBOutlet id passwordField;
	IBOutlet id tagListField;
	IBOutlet id itemsPerFeedSlider;
	IBOutlet id itemsPerFeedLabel;
	
	IBOutlet id tagListNavItem;
	IBOutlet id stopEditingFeedsButton;

	IBOutlet id accountNavItem;
	IBOutlet id stopEditingAccountButton;
	
	IBOutlet id showReadItemsToggle;
	IBOutlet id rotationLockToggle;
	IBOutlet id openLinksInSafariToggle;
	IBOutlet id newestItemsFirstToggle;
	BOOL rotationLock;
	
	IBOutlet id feedList;
	IBOutlet id noFeedsView;
	IBOutlet id feedSelectionView;
	IBOutlet id feedsPlaceholderView;
}
-(NSString *) docsPath;
-(NSString *) email;
-(NSString *) password;
-(int) itemsPerFeed;

- (IBAction) itemsPerFeedDidChange: (id) sender;
- (IBAction) stringValueDidChange:(id)sender;
- (IBAction) switchValueDidChange:(id) sender;

- (IBAction) activatePasswordField:(id)sender;
- (IBAction) deactivateBothFields:(id)sender;
- (IBAction) textFieldDidEndEditing:(UITextField *)sender;
- (IBAction) deactivateTagListField:(id) sender;
@end
