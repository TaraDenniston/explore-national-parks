"use strict";

const BASE_URL = 'https://developer.nps.gov/api/v1/'
const KEY = 'jako3waTKpoJF9s75DqqN7lXiVrxxIPVTIGKHT3L'


/******************************************************************************
 *  Activity: a single activity
 *****************************************************************************/
class Activity {
  constructor({id, name}) {
    this.id = id;
    this.name = name;
  }
}