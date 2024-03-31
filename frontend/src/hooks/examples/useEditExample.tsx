'use client'
import {useState} from 'react'
import {Form} from '@/types/Forms'
import {BASE_URL} from '@/constants/url'
import {useKindeBrowserClient} from '@kinde-oss/kinde-auth-nextjs'

const useEditExample = (formId: string) => {
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState(null)
    const {accessTokenEncoded} = useKindeBrowserClient()

    const editExample = async (exampleId: string, data: string) => {
        const headers = {
            'Authorization': `Bearer ${accessTokenEncoded}`,
            'Content-Type': 'application/json',
        }
        setIsLoading(true)
        setError(null)
        try {
            const response = await fetch(
                `${BASE_URL}/automatic-responses/${formId}/example/${exampleId}`,
                {
                    method: 'PATCH',
                    headers: headers,
                    body: JSON.stringify({
                        example: data,
                    }),
                }
            )
            setIsLoading(false)
            return await response.json()
        } catch (error: any) {
            setError(error)
            setIsLoading(false)
            throw error
        }
    }

    return {editExample, isLoading, error}
}

export default useEditExample
