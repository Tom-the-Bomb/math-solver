import List from "./List";

function Input({placeholder, height}) {
    return (
        <textarea
            className={
                `block ${height} w-full resize-none font-serif
                my-input text-lg  border-t-2 border-red-900`
            }
            placeholder={placeholder}
            type="text"
            name="equation"
            spellCheck="false"
            autoCorrect="false"
            autoCapitalize="false"
            data-gramm="false" data-gramm_editor="false" data-enable-grammarly="false"
        />
    )
}

function Form() {
    function handleSubmit(event) {
        event.preventDefault();

        const elements = event.target.elements;
        const equation = elements.equation.value;
        
        const arr = Array(elements);
        const functions = arr
            .map(x => {
                console.log('AAA', x)
                console.log('BBB', x.name)
            });
        
        //console.log(functions);
        console.log(equation);
        /*
        fetch(
            'localhost:5000/solve', {
                method: 'POST',
                mode: 'cors',
                body: JSON.stringify({

                })
            }
        )*/
    }

    return (
        <form className="flex flex-col h-full w-full justify-between" onSubmit={handleSubmit}>
            <div className="flex flex-col gap-10 p-10 overflow-y-auto">
                <List type="Functions"></List>
                <List type="Constants"></List>
            </div>
            <div className="h-1/2 w-full self-end inline-block relative">
                <span class="sr-only">Search</span>
                <Input
                    placeholder={"Enter an equation..."}
                    height={"h-full"}>
                </Input>
                <button
                    className="my-focus my-hover text-gray-100 bg-green-500
                    rounded-lg p-3 absolute bottom-[5%] right-8"
                    type="submit"
                >Enter</button>
            </div>
        </form>
    )
}

export default function Main() {
    return (
        <main className="grow grid grid-cols-2 flex-wrap">
            <div className="bg-red-1 drop-shadow-2xl">
                <Form></Form>
            </div>
            <div className="bg-red-2 p-10">
                <h1 className="my-h1">Output</h1>
            </div>
        </main>
    )
}