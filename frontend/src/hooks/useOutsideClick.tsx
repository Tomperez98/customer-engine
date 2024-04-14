import {RefObject, useEffect} from 'react'

type Callback = () => void

export const useOutsideClick = (
    ref: RefObject<HTMLElement>,
    callback: Callback
) => {
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (ref.current && !ref.current.contains(event.target as Node)) {
                callback()
            }
        }
        document.addEventListener('mousedown', handleClickOutside)
        return () => {
            document.removeEventListener('mousedown', handleClickOutside)
        }
    }, [ref, callback])
}
