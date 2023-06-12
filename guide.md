# Solver Usage Guide
- **Builtins**
	
## Syntax Specifications
This document contains specifications for valid syntax structures and patterns for the solver's parser.
- **Equation**
Parses an equation; used in the primary equation input.
An equation is a relation between 2 expressions:<br>
`<expr> "="|"!="|">"|">="|"<"|"<=" <expr>`
*If only an* `<expr>` *is supplied,*
*the parser will be default assume that* `<expr> = 0`.
	- **`<expr>`**
		Parses a mathematical expression, this is a general parser node
		used throughout the parser.
		- **Unary minus**
			Negates the expression  
			
			Syntax: `"-" <group>` 
			Ex: `-x`
			
		- **Binary operations**
			Basic binary arithmetic operations 
			
			Syntax: `<expr> "+"|"-"|"*"|"/"|"%"  <expr>` 
			Ex: `2x + 1`
			
		- **Summation**
			Syntax: `"sum_(" <var> "=" <group>) "^" <group> <group>` 
			Ex: `sum_(n=0)^10 x` -> $\sum_{0}^{10}x$
		- **Product**
			Syntax: `"prod_(" <var> "=" <group>) "^" <group> <group>` 
			Ex: `prod_(n=0)^10 x` -> $\prod_{1}^{10}x$
		- **Absolute value**
			Syntax: `"|" <expr> "|"` 
			Ex: `|x + 1|` -> $|x + 1|$ 
			
			Can also be used by calling the `abs` function: `abs(x)`
			
		- **`<group>`**
		represents a group of mathematical symbols and terms that can be interpreted together as one group without the need for explicit grouping.
			- **Explicit grouping**
				An `<expr>` surrounded by a corresponding pair
				of either `()`, `[]` or `{}`
			- **Number** `<number>`
				A numerical value, satisfied by the following regex:
				`/([0-9]+(\.[0-9]*)?|\.[0-9]+)/`	
				Ex: `123`, `14.6`
			- **Variable** `<var>`
				Represents a variable or an *access* of a constant that is included in **builtins** or user defined.
				Syntax: `<identifier>`
				*or* `<identifier> "_" <number>` for associated subscript values.
				Ex: `x`, `x_0` -> $x_0$
			- **Function Call** `<func>`
			 A call to a predefined function, either one included in **builtins** (E.g. `sin`, `floor`...) or a user defined function.
				
				Syntax: `<identifer> "(" expr, ...")"`
				
				NOTE: function calls must be surrounded by explicit parentheses `()` and expressions like `sin x ` are not allowed, instead use `sin(x)`.
				- **Subscripted Function**
				Syntax: `"_" (number | <var> | <explicit grouping>)`
				in between the *identifer* and *call* of a standard function call
				Ex: `log_x(y)` -> $log_xy$ | `log_(2x)(y)` -> $log_{2x }y$
			- **Exponentiation**
			*Separate from **Binary Operations** as it takes `<group>` for operands.*
			Syntax: `<group "^" <group>`
			Ex: `x^3` -> $x^3$
			- **Limit**
			Syntax: `"lim_(" <group> "->" <expr> ")" <group>`
			Ex: `lim_(h->0)(x + h)` -> $\lim\limits_{h\to0} (x+h)$
			- **Custom root**
			Syntax: `"root" <group> <group>`
			Ex: `root3(x + 1)` -> $\sqrt[3]{x+1}$<br>
			Can also be accessed via the `rt` function:
			`rt(x, 3)` -> $\sqrt[3]{x}$
			- **Factorial**
			Syntax: `"<group>"!"`
			Ex: `x!` or `(x + 1)!`<br>
			Can also be accessed via the `factorial` function: `factorial(x)`
			- **Implicit Multiplication** 
			Adjacent terms that do not satisfy other parser rules will be inferred to be implicit multiplication:
			<br>Syntax: `<group> <group>`
			Ex: `3(x + 1)2x` -> $3\cdot\left(x + 1\right)\cdot2\cdot x$

- **Domain**
	Parses a domain expression
	- **Interval** `<Interval>`
		- An mathematical interval notation
		- `<expr>, <expr>` surrounded by either *square brackets* or *parentheses*
		- Ex: `[0, inf)`
	- **Number set** `<number_set>`
		- One of the number sets in mathematics, represented by their full name or their mathematical abbreviation
		- `Complex | Real | Rational | Integer | Whole | Natural`
		- `C | R | Q | Z | W | N`
	- **Compound** `<number_set> "|" <Interval>`
		- A combination of the above expressions joined by a `|` operator, representing an intersection of the above 2 sets.
- **Function**
Parses a declared function expression
	- `<func> "=" <expr>`
		- Ex: `f(x) = 2x + 1`
	- Added to **builtins** and can be later called in the primary equation
- **Constant**
	A custom constant AKA a variable input / alias
	- **name**
	The `name` of the constant, a valid `<var>`
	- **value**
	The value of the constant, any valid number.
	(NO additional parsing is done on this field)