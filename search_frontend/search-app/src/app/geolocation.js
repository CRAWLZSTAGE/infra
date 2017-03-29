if ("geolocation" in navigator) {
	navigator.geolocation.getCurrentPosition(function(position) {
	  console.log(String(position.coords.latitude) + " : " +  String(position.coords.longitude));
	  localStorage.lat = position.coords.latitude;
	  localStorage.lon = position.coords.longitude;
	});
}