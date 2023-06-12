# Solver Usage Guide<br>
A guide on the syntax of solver inputs<br>
<br>
## Syntax Specifications<br>
This document contains specifications for valid syntax structures and patterns for the solver's parser.<br>
- ### Equation
	Parses an equation; used in the primary equation input.<br>
	An equation is a relation between 2 expressions:<br>
	`<expr> "="|"!="|">"|">="|"<"|"<=" <expr>`<br><br>
	*If only an* `<expr>` *is supplied,*<br>
	*the parser will be default assume that* `<expr> = 0`.<br><br>
	- ### Expression: `<expr>`<br>
		Parses a mathematical expression, this is a general parser node<br>
		used throughout the parser.<br><br>
		- **Unary minus**<br>
			Negates the expression<br>
			Syntax: `"-" <group>`<br>
			> Ex: `-x`<br>
		- **Binary operations**<br>
			Basic binary arithmetic operations <br>
			Syntax: `<expr> "+"|"-"|"*"|"/"|"%"  <expr>` <br>
			> Ex: `2x + 1`<br>
		- **Summation**<br>
			Syntax: `"sum_(" <var> "=" <group>) "^" <group> <group>` <br>
			> Ex: `sum_(x=0)^10 x` &#8594; $\sum\limits_{x=0}^{10}x$<br>
		- **Product**<br>
			Syntax: `"prod_(" <var> "=" <group>) "^" <group> <group>` <br>
			> Ex: `prod_(x=0)^10 x` &#8594; $\prod\limits_{x=1}^{10}x$<br>
		- **Absolute value**<br>
			Syntax: `"|" <expr> "|"`<br>
			> Ex: `|x + 1|` &#8594; $|x + 1|$<br>
			- Can also be used by calling the `abs` function: `abs(x)`<br><br>
		- ### Group: `<group>`<br>
			represents a group of mathematical symbols and terms that can be interpreted together as one group without the need for explicit grouping.<br><br>
			- **Explicit grouping**<br>
				An `<expr>` surrounded by a corresponding pair<br>
				of either `()`, `[]` or `{}`<br><br>
			- **Number** `<number>`<br>
				A numerical value, satisfied by the following regex:<br>
				`/([0-9]+(\.[0-9]*)?|\.[0-9]+)/`<br>
				> Ex: `123`, `14.6`<br>
			- **Variable** `<var>`<br>
				Represents a variable or an *access* of a constant that is included in **builtins** or user defined.<br>
				Syntax: `<identifier>`<br>
				*or* `<identifier> "_" <number>` for associated subscript values.<br>
				> Ex: `x`, `x_0` &#8594; $x_0$<br>
			- **Function Call** `<func>`<br>
			A call to a predefined function, either one included in **builtins** (E.g. `sin`, `floor`...) or a user defined function.<br>
				Syntax: `<identifer> "(" expr, ...")"`<br>
				<br>
				**NOTE:** function calls must be surrounded by explicit parentheses `()` and expressions like `sin x ` are not allowed, instead use `sin(x)`.<br>
				- **Subscripted Function**<br>
                    Syntax: `"_" (number | <var> | <explicit grouping>)`<br>
                    in between the *identifer* and *call* of a standard function call<br>
                    > Ex: `log_x(y)` &#8594; $log_xy$ | `log_(2x)(y)` &#8594; $log_{2x }y$<br>
			- **Exponentiation**<br>
                *Separate from **Binary Operations** as it takes `<group>` for operands.*<br>
                Syntax: `<group> "^" <group>`<br>
                > Ex: `x^3` &#8594; $x^3$<br>
			- **Limit**<br>
                Syntax: `"lim_(" <group> "&#8594;" <expr> ")" <group>`<br>
                > Ex: `lim_(h->0)(x + h)` &#8594; $\lim\limits_{h\to0} (x+h)$<br>
			- **Custom root**<br>
                Syntax: `"root" <group> <group>`<br>
                > Ex: `root3(x + 1)` &#8594; $\sqrt[3]{x+1}$<br>
                - Can also be accessed via the `rt` function:<br>
                `rt(x, 3)` &#8594; $\sqrt[3]{x}$<br>
			- **Factorial**<br>
			    Syntax: `"<group>"!"`<br>
                > Ex: `x!` or `(x + 1)!`<br>
                - Can also be accessed via the `factorial` function: `factorial(x)`<br>
			- **Implicit Multiplication** <br>
                Adjacent terms that do not satisfy other parser rules will be inferred to be implicit multiplication:<br>
                Syntax: `<group> <group>`<br>
                > Ex: `3(x + 1)2x` &#8594; $3\cdot\left(x + 1\right)\cdot2\cdot x$<br>

- **Domain**<br>
	Parses a domain expression<br>
	- **Interval** `<Interval>`<br>
		- An mathematical interval notation<br>
		- `<expr>, <expr>` surrounded by either *square brackets* or *parentheses*<br>
		- Ex: `[0, inf)`<br>
	- **Number set** `<number_set>`<br>
		- One of the number sets in mathematics, represented by their full name or their mathematical abbreviation<br>
		- `Complex | Real | Rational | Integer | Whole | Natural`<br>
		- `C | R | Q | Z | W | N`<br>
	- **Compound** `<number_set> "|" <Interval>`<br>
		- An intersection of the above expressions joined by a `|` operator, representing a combination of the above 2 sets.<br>
- ### Function
	Parses a declared function expression<br>
	- `<func> "=" <expr>`<br>
		- Ex: `f(x) = 2x + 1`<br>
	- Added to **builtins** and can be later called in the primary equation<br>
- ### Constant
	A custom constant AKA a variable input / alias<br>
	- **name**<br>
	The `name` of the constant, a valid `<var>`<br>
	- **value**<br>
	The value of the constant, any valid number.<br>
	(NO additional parsing is done on this field)
