// Enable JavaScript's strict mode. Strict mode catches some common
// programming errors and throws exceptions, prevents some unsafe actions from
// being taken, and disables some confusing and bad JavaScript features.
"use strict";

 this.ckan.module('hide_id', function ($, _) {
  return {
    initialize: function () {
       $("#field-id").parent().parent().hide();
       $("#field-id").attr("readonly",true);
    }
  };
});