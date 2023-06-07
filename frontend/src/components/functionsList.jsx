import { useState } from 'react';

function Input({placeholder}) {
    return (
        <input className="rounded-md text-xs my-input h-16 w-[50%]" type="text" placeholder={placeholder}></input>
    )
}

function Fx({func}) {
    return (
        <div className="justify-self-center">
            <Input placeholder="E.g. f(x) = 2x ..."></Input>
        </div>
    )
}

export default function FunctionsList() {
    const list = ["a", "b", "c"]
    const [ funcs, setFunctions ] = useState(list);

    const add = () => {
        let copy = [...funcs];
        copy = [...copy , "a"];
        setFunctions(copy);
    }

    return (
        <div className="flex flex-col ml-10 mt-10 margin-10 gap-3 overflow-y-scroll">
            <h1 className="text-white font-sans font-bold text-2xl">Functions</h1>
            {funcs.map(fx => {
                return (
                    <Fx func={fx}/>
                )
            })}
            <button type="button" onClick={add}>TEST</button>
        </div>
    )
}