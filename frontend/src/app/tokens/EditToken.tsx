import Button from '@/components/Button'
import EditableInputField from '@/components/EditableInputField'
import {TOKEN_FIELDS, TOKEN_TEMPLATE} from '@/constants/tokenFields'
import {BASE_URL} from '@/constants/url'
import useDeleteToken from '@/hooks/tokens/useDeleteToken'
import useEditToken from '@/hooks/tokens/useEditToken'
import {Token, TokenKey, TokenKeys, TokenTemplate} from '@/types/Tokens'
import {
    validateFormHasChanges,
    validateNoEmptyFields,
} from '@/utils/validateFormFields'
import {useEffect, useState, useMemo} from 'react'

interface EditTokenProps {
    setShouldRefetch: (shouldRefetch: boolean) => void
    token: Token
}

const EditToken = ({setShouldRefetch, token}: EditTokenProps) => {
    const [editableTokenTemplate, setEditableTokenTemplate] =
        useState(TOKEN_TEMPLATE)
    const [isEditingToken, setIsEditingToken] = useState<boolean>(false)
    const [resetAllFormFields, setResetAllFormFields] = useState<boolean>(false)
    const tokenData = useMemo(() => token, [token])
    const {deleteToken} = useDeleteToken()
    const {
        submit,
        isLoading: isUpdateLoading,
        error,
    } = useEditToken(editableTokenTemplate)

    const relevantData = useMemo(() => {
        return Object.keys(TOKEN_TEMPLATE).reduce(
            (acc, key) => {
                if (token?.hasOwnProperty(key)) {
                    acc[key] = tokenData[key as TokenKey]
                }
                return acc
            },
            {} as {[key: string]: string | string[]}
        )
    }, [token, tokenData])

    const areChangesValid =
        validateNoEmptyFields(editableTokenTemplate) &&
        validateFormHasChanges(
            editableTokenTemplate,
            relevantData as TokenTemplate
        )

    const handleSaveChanges = async () => {
        setIsEditingToken(false)
        await submit()
        setShouldRefetch(true)
        setResetAllFormFields(true)
    }

    const handleDeleteToken = async () => {
        await deleteToken()
        setShouldRefetch(true)
    }

    useEffect(() => {
        if (token) {
            setEditableTokenTemplate({...(relevantData as TokenTemplate)})
        }
    }, [token, relevantData])

    const webhookUrl = `https://api-staging-54f3.up.railway.app/webhooks/whatsapp/${token.org_code}`

    return (
        <div className='flex w-full flex-col flex-wrap gap-4 text-wrap'>
            <div>
                <label
                    htmlFor='automatic_response_id'
                    className='text-lg font-semibold capitalize text-neutral-800'>
                    {TokenKeys['webhook_url']}
                </label>
                <p>{webhookUrl}</p>
            </div>
            {TOKEN_FIELDS.map((field, idx: number) => {
                return (
                    <EditableInputField
                        fieldName={field.name as TokenKey}
                        template={editableTokenTemplate}
                        isEditingTemplate={isEditingToken}
                        key={idx}
                        label={field.label}
                        originalValue={tokenData[field?.name as TokenKey]}
                        setTemplate={setEditableTokenTemplate}
                        setIsEditingTemplate={setIsEditingToken}
                        souldForceReset={resetAllFormFields}
                        type='input'
                    />
                )
            })}
            {isEditingToken && (
                <div className='mt-4 flex w-full flex-row items-center justify-end gap-4'>
                    <Button
                        onClick={handleDeleteToken}
                        label='Borrar'
                        style='secondary'
                    />
                    <Button
                        disabled={!areChangesValid}
                        onClick={handleSaveChanges}
                        label='Guardar'
                    />
                </div>
            )}
        </div>
    )
}

export default EditToken
