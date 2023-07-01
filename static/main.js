"use strict";

const $activities = $('#activities');
// const $familyDetails = $('#family-details');
// let currentUser;


/**********************************************************************************
 *  Get list of activities from NPS API
 *
 *  Returns array objects that contain: 
 *  {id, activityName}
 **********************************************************************************/
async function getActivities() {
  console.log('inside getActivities()');
  let activities = [];
  
//   // make GET request to NPS API
//   await $.get( `${BASE_URL}/activities`, function( data ) {

  //make GET request to NPS API
  const response = await axios({
    url: `${BASE_URL}/activities`,
    method: 'GET',
    headers: {
        'Authorization': `X-Api-Key: ${KEY}`
    }
  });

  console.log(`response: ${response}`);
  let properties = Object.getOwnPropertyNames(response);
  console.log(`typeof(response): ${typeof(response)}`)
  console.log(`properties of response: ${properties}`);
  
//   console.log(data);
//   // from the result, create an Activity object  
//   activity = new Activity({
//     id: data.id,
//     name: data.name,
//   });  
  
//   console.log(activities[0]);
  
  return activities;
}


/**********************************************************************************
 * Display details on DOM
 * 
 * Calls getMhUserInfo() and displays returned information about user in the user
 * details section
 **********************************************************************************/
async function displayDetails() {

  // Get list of activities from the API
  let activities = await getActivities();
  
  // // Display user info on the DOM
  // displayUser(user);
  
    // // Get family info from the API
    // console.log(`Individual ID: ${user.individual}`)
    // let family = await createFamily(user.individual);
  
    // let properties = Object.getOwnPropertyNames(family);
    // console.log(`family: ${family}`)
    // console.log(family);
    // console.log(`typeof(family): ${typeof(family)}`)
    // console.log(`properties of family: ${properties}`);
  
    // displayFamily(family);
}


/**********************************************************************************
 * When document has finished loading, execute the display function 
 **********************************************************************************/
$(function() {
  displayDetails();
});