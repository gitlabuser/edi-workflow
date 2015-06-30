Feature: Partner creation
	I create a new partner and I mark it as
	EDI relevant, I expect the necesarry EDI folders
	to be created for each EDI flow this partner
	is subscribed to.


	Scenario: Create an EDI partner
    	Given an EDI relevant partner
    	Then a partner should have been created
   		And the partner should be EDI relevant
   		And a folder should have been created

   	Scenario: Assign EDI flows to a partner
   		Given an EDI relevant partner
   		When this partner is assigned an incoming and outgoing flow
   		Then the flows should be assigned to the partner
   		And the EDI folders should be created on the system

	Scenario: Delete leftover data from a previous test
		Given partners have already been created
