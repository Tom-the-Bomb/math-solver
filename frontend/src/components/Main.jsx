
import FunctionsList from "./functionsList";

function Input({placeholder, height}) {
    return (
        <textarea
            className={
                `block ${height} w-full resize-none font-serif
                my-input text-lg`
            }
            placeholder={placeholder}
            type="text"
            name="search"
            spellCheck="false"
            autoCorrect="false"
            autoCapitalize="false"
            data-gramm="false" data-gramm_editor="false" data-enable-grammarly="false"
        />
    )
}

function Form() {
    function handleSubmit(event) {
        event.preventDefault()
    }

    return (
        <form className="flex flex-col h-full w-full justify-between" onSubmit={handleSubmit}>
            <FunctionsList></FunctionsList>
            <div className="h-[50%] w-full self-end inline-block relative">
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
        <main className="grow grid grid-cols-2">
            <div className="bg-red-1 drop-shadow-2xl">
                <Form></Form>
            </div>
            <div className="bg-red-2">

            </div>
        </main>
    )
}