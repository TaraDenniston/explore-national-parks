"use strict";


const $body = $("body");


// Listen for click on all star icons
async function toggleFavorite(evt) {
  evt.preventDefault();

  const $star = $(evt.target);

  // Fetch data from the target
  const parkCode = $star.data("park");
  const userId = $star.data("user");
  const url = $star.data("url");
  let favValue = $star.data("fav");

  // Set new favorite value
  let newFavValue = !favValue;

  // Only update if a user is logged in
  if(userId) {
    const favData = `{"park":"${parkCode}", "user":"${userId}", "favValue":"${newFavValue}"}`

    // Make a post request to update favorite status
    $.ajax({
      type: "POST",
      contentType: 'application/json',
      url: url,
      dataType: 'json',
      data: JSON.stringify(favData)
    });

    // If park is not favorited, toggle attributes on
    if (!favValue) {
      $star.attr("class", "fav fa-solid fa-star");
      $star.attr("style", "color: #f7d702;");
      $star.data("fav", "true");
    }

    // If park is already favorited, toggle attributes off
    if (favValue) {
      $star.attr("class", "fav fa-regular fa-star");
      $star.attr("style", "color: #bababa;");
      $star.data("fav", "false");
    }
  } 
}


/**********************************************************************************
 * When document has finished loading, execute the functions
 **********************************************************************************/
$(function() {
  $('[data-toggle="tooltip"]').tooltip();
  $('[data-toggle="popover"]').popover();
  $body.on("click", "i.fav", toggleFavorite);
});