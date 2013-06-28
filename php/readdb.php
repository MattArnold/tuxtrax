<?php

$dbhost = 'localhost';
$dbuser = 'penguintrax_user';
$dbpass = 'randomgibberish';
$dbname = 'penguintrax';



$dbconn = new mysqli($dbhost, $dbuser, $dbpass, $dbname);

$query  = "SELECT * FROM $penguintrax.events;";
$result = $dbconn->query($query);
$num1   = $result->num_rows;

$query  = "SELECT * FROM $dbname.kucourses;";
$result = $dbconn->query($query);
$num2   = $result->num_rows;

$query  = "SELECT * FROM $dbname.schools;";
$result = $dbconn->query($query);
$num3   = $result->num_rows;

$dbconn->close();

printf("%d total guest courses transferable to %d unique Kettering courses from %d schools.", $num1, $num2, $num3);

?>