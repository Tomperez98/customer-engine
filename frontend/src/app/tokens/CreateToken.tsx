import {TOKEN_FIELDS, TOKEN_TEMPLATE} from '@/constants/tokenFields'
import {ChangeEvent, useCallback, useState} from 'react'
import {TokenTemplate, TokenKey} from '@/types/Tokens'
import {InputName} from '@/types/Inputs'
import Input from '@/components/Input'
import Button from '@/components/Button'
import {
    validateAllEmptyFields,
    validateNoEmptyFields,
} from '@/utils/validateFormFields'
import useCreateToken from '@/hooks/tokens/useCreateToken'

interface CreateTokenProps {
    setShouldRefetch: (shouldRefetch: boolean) => void
}

const CreateToken = ({setShouldRefetch}: CreateTokenProps) => {
    const [tokenTemplate, setTokenTemplate] =
        useState<TokenTemplate>(TOKEN_TEMPLATE)
    const {submit} = useCreateToken(tokenTemplate)
    const handleTokenFieldChange = (
        event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
        name: InputName
    ) => {
        setTokenTemplate((prevState) => ({
            ...prevState,
            [name]: event.target.value,
        }))
    }

    const handleCreateForm = useCallback(async () => {
        await submit()
        setShouldRefetch(true)
    }, [submit])

    return (
        <div>
            <div className='flex flex-col gap-4'>
                {TOKEN_FIELDS.map(({name, label}, idx) => {
                    return (
                        <div className='flex flex-col gap-2' key={idx}>
                            <label
                                htmlFor='automatic_response_id'
                                className='text-lg font-semibold capitalize text-neutral-800'>
                                {label}
                            </label>
                            <Input
                                name={name as TokenKey}
                                onChange={handleTokenFieldChange}
                                value={tokenTemplate[name as TokenKey] || ''}
                            />
                        </div>
                    )
                })}
            </div>
            <div className='mt-4 flex w-full flex-row items-center justify-end gap-4'>
                <Button
                    label='Descartar'
                    onClick={() => setTokenTemplate(TOKEN_TEMPLATE)}
                    style='secondary'
                    disabled={validateAllEmptyFields(tokenTemplate)}
                />
                <Button
                    disabled={!validateNoEmptyFields(tokenTemplate)}
                    label='Guardar'
                    onClick={handleCreateForm}
                />
            </div>
        </div>
    )
}

export default CreateToken
