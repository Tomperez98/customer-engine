'use client'

import {useEffect, useRef, HTMLProps} from 'react'

const IndeterminateCheckbox = ({
    indeterminate,
    className = '',
    ...rest
}: {indeterminate?: boolean} & HTMLProps<HTMLInputElement>) => {
    const ref = useRef<HTMLInputElement>(null!)

    useEffect(() => {
        if (typeof indeterminate === 'boolean') {
            ref.current.indeterminate = !rest.checked && indeterminate
        }
    }, [ref, indeterminate])

    return (
        <input
            type='checkbox'
            ref={ref}
            className={className + ' cursor-pointer'}
            {...rest}
        />
    )
}

export default IndeterminateCheckbox
