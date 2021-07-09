# PHP programming language 

PHP is one of the most commonly used languages to generate dynamic websites.

!["PHP logo"](php.jpg)

Here are some basic notions about the PHP language, to which I am totally 
new. For more information, see [this lecture](https://youtu.be/OK_JCtrrv-c)
about the PHP language. 


## Getting started  

PHP needs to be run on a web server. In order to create the server that will 
support the code, we must use the following command : 

```
php -S localhost:4000
```

The associated files will be found in the folder `/home/ludivine/www` (on the Linux machine). 

We must generate an HTML skeleton for the file in order for the PHP script to be read and integrated into the web server. 

To write PHP inside an HTML script, we need to use the PHP tag `<?php` at the start of the code and `?>` and the end. 

> At the end of each instruction, we MUST put `;` 


A variable in PHP is identified by a `$`. For instance: 
```
$characterName = "Gloria";  // this is a string
$age = 22;  // this is an integer 
$grade = 16.25;  // this is a decimal or float
$is Hungry = false;  // this is a boolean 
```
We can also encounter `null`, which means that there is no value. 

## Some basic functions 

#### echo 

*echo* enables the PHP code to be printed in the HTML file. We can even include HTML commands into a PHP tag. 

```
echo "test";  // same thing as echo("test")
echo "<p> this is a test </p>";
```

#### String operations 

* *strtolower*: when used on a string, all the letters are lowered;
* *strtoupper*: when used on a string, all the letters become capital letters; 
* *strlen*: returns the length of the string;
*  *strreplace("old_word", "new_word", "string")*: replaces a certain sequence of characters by another; 
*  *substr("string", starting_index, length)*: grabs a part of a given string; 

We can index a string, meaning if we want to know what is character number i of a given string, we must use:
```
$phrase = "This is a phrase";
echo $phrase[0];
```

> In PHP, just like in Python, indexing begins at 0. 


#### Number operations 

* *x%y*: returns the remainer of the division of x by y;
* *$num++ or --*: increments by +1 or -1 the number;
* *pow(x, y)*: returns x^y;
* *floor() and ceil()*: returns the entire part of a number, either to the lower or the upper int  


## Getting user input 

#### get

First, we need to set up an HTML form which enables the user to interact with the code:
```
<form action="nameFile.php" method="get> 
  Name: <input type="text" name="name">
  <input type="submit">
</form>
```

* *method* refers to what kind of action we want to perform (here, we want to gather information from the user);
* *input* refers to elements of the site that the user will be able to interact with:
  * `type="text"` creates a textbox 
  * `type="submit"` creates a submit button 

> In the declaration of the form, we can also put `step=0.0..01` if we want the HTML code to handle a floating number with a given number of decimals. By default, `type="number"` only handles integers. 

Then, we must get the information from the user in the PHP script: 
```
<?php $_GET["name"] ?>
```

The method `$_GET` is populated by the value that the user submitted on the web page. 

> The information given by the user can be seen in the URL : 
> 
>    `localhost:4000/www/site.php?name="John"`
>    
> This is called a **URL variable**. We can directly add variables in the URL and manipulate it in the PHP code. 
> The problem with this method is that it lacks security (the user can see AND change the values of the variables. 


#### post 

In the HTML, we can change the methode from *get* to *post*. 
This way, the value submitted by the user does not show up in the url. It is quite interesting in the case of passwords for instance: 

```
<form action="site.php" method="post">
  <input type="password" name="password">
</form>

THEN 

<?php echo $_POST["password"]; ?>
```

## Arrays 

An array is quite similar to a variable, but contrary to it, it can store numerous values. 

To create an array:

```
$arrayName = array(a, b, c, d);
```
with a, b, d and d being whatever variable type we want. 

Just like strings, the elements in an array are indexed and can be accessed by the following instruction:

```
$arrayName[x]  // x ranging from 0 to len($arrayName)
```
To access the number of elements contained in a given array : `count($arrayName)`


#### Checkboxes 

This is a great way to interact with the user and gather some information. 

```
<form action="site.php" method="post">
  Val1: <input type="checkbox" name="array[]" value="val1"><br>
  Val2: <input type="checkbox" name="array[]" value="val2"><br>
  Val3: <input type="checkbox" name="array[]" value="val3"><br>
</form>
```

To get the information in the PHP script:
```
<?php $array = $_POST["array"]; ?> 
```

#### Associative arrays 

This is quite similar to a dictionary in Python: we can store key values pairs in such an array. 

```
$dict = array(key1=>val1, key2=>val2);
```

To access to an element:
```
$dict[key1];
```
It will return the value associated to the key n°1. 

> We need to make sure that each key is unique. 


## Function 

A **function** in PHP is just like in Python or any other language: it is a part of code that is designed to execute one particular task. 

First we define the function and what it does: 
```
  function nameFunction($parameters){
    // insert task // 
    // we can return the result of the function :
    return $returnParam
  }
```
Then we must call it so that it executes:
```
nameFunction($parameters);
```

> The *return* keyword MUST be put at the very end of the function, otherwise the instructions written after it won't be executed! 


## IF statement 

The PHP syntax for an IF statement is the following: 

```
if (condition1){
  // task to be executed //
} elseif (condition2){
  // task to be executed 
} else {
  // task to be executed otherwise //
}
```

In the condition, we can put `&&` which corresponds to AND, or `|| which signifies OR. 

> The `!` is the negative sign: if we declare a variable `$bool = true` and type in `$bool = !$bool` then `$bool` has become false.


## Switch statements 

A **switch statement** is used when we want to compare a variable to a certain set of possible values. 

```
switch($val){
  case "case1":
    // task //
    break;
  case "case2":
    // task //
    break;
  default:
    // task to execute when none of the cases are true //
}
```

## Loops

#### While loop

The **while loop** is used to loop over a certain block of code while a certain condition is true. 

```
while(loop condition){
  // loop body //
  // task to execute //
}
```

An alternative while loop is the following:

```
do{
  // task to execute //
}while (loop condition)
```

The main difference is that the order is reversed: first the loop body is executed, then the loop condition is checked. 

#### For loop 

The **for loop** is similar to other for loops in other languages. The PHP syntax is quite the same as the one for the while loop:

```
for(loop condition){
  // loop body //
  // task to execute //
}
```

In the parentheses of the loop declaration, we put:
* the initial value of the indexing parameter (e.g. `$i=1`);
* the looping condition (e.g `$i <= 5`);
* the code that we want to be executed at each iteration of the loop (in most cases, incrementation of the index).

The syntax is therefore as follows:
```
for($i=1; $i <= 5; $i++){...}
```


## Including HTML and PHP

The keyword **include** is used when we want to use another file within the PHP script. 

To include an HTML or PHP file, we use the following instruction:
```
include "nameFile.html" OR "nameFile.php";
```

The files that are included this way must be located in the same folder as the main PHP file. 

When we include other files in the main PHP script, we can use the same variables in the different files, as long as they *have the same name* in all the files. 


## Classes and objects 

The idea behind **classes** is that some objects cannot be represented just by a simple variable; in this case, we can create our own custom data type in order to model an object that we will manipulate. 

For instance, if we want to create a class *Book*:

```
class Book {
  var $title;
  var $author;
  var $pages; 
}
```

Then, to create an **object** belonging to the *Book* class:

```
$book1 = new Book; 
$book1->title = "Harry Potter";
$book1->author = "JK Rowling";
$book1->pages = 532;
```

#### Constructor 

A **constructor** is a function that is called whenever we create an object of the class. It is usually used to initiate the class parameters. It must be defined within the class script: 

```
function __construct($aTitle, $aAuthor, $aPages){
 $this->title = $aTitle; 
 $this->author = $aAuthor;
 $this->pages = $aPages; 
}
```

`this` is a key word that refers to the current object. 

#### Object function

An **object function** is a function that is defined inside of a class and that can be used by the objects belonging to the class. 

To call an object function, we use the following instruction: 
```
$object->nameFunction($attributes);
```

#### Accessibility of the attributes 

In other words, we want to be able to control the attributes declared by a user when creating a new object, so that they belong to an acceptable set of values. 

In order to do so, we can use the followings:
* *Visibility modifiers* are keywords that define whether or not a user have access to the attributes:
  * `public` means that it is visible to anyone using the PHP script (it is similar to `var`);
  * `private` means that any code outside of the class code cannot have access to the attribute. 

* *Getters and setters* are functions that allow us to control the accessibilty of the attributes: 

```
// A getter enables the user to have access to the value of an attribute //
function getAttribute(){
  return $this->attribute;
}

// A setter allows the user to change the value of an attribute //
function setAttribute($value){
  $this->attribute = $value
}
```

Inside of the setter function, we can implement rules so that the value of the attribute belongs to an acceptable range of values. 

#### Inheritance 

The concept of **inheritance** means that a class can inherit all of the functionality and attributes of another class in PHP . 

```
class SpecialisedClass extends Class {
  // new functions of the specialised class //
}
```

If an object of the SpecialisedClass is created, it can access all the functions of the Class, plus the functions defined in the SpecialisedClass. 

It is also possible to *override* a function from one class to another: by using the same function name in SpecialisedClass than in Class, we can update the definition of the function in the case of the SpecialisedClass. 

