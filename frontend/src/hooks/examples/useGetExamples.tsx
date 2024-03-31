import {useEffect, useState} from 'react'
import {BASE_URL} from '@/constants/url'
import {useKindeBrowserClient} from '@kinde-oss/kinde-auth-nextjs'
import {Example} from '@/types/Examples'

export type ExampleResponse = {
    examples: Example[]
}

const useGetExamples = (formId?: string) => {
    const [data, setData] = useState<ExampleResponse>()
    const [isLoading, setIsLoading] = useState<boolean>(false)
    const {accessTokenEncoded} = useKindeBrowserClient()

    const fetchExamples = async () => {
        if (!accessTokenEncoded) return
        const headers = {
            Authorization: `Bearer ${accessTokenEncoded}`,
        }
        setIsLoading(true)

        try {
            const res = await fetch(
                `${BASE_URL}/automatic-responses/${formId}/example`,
                {
                    headers: headers,
                }
            )
            const resJson = await res.json()

            setData(resJson)
        } catch (error) {
            console.log(error)
        } finally {
            setIsLoading(false)
        }
    }

    useEffect(() => {
        if (accessTokenEncoded) {
            fetchExamples()
        }
    }, [accessTokenEncoded])

    const refetch = () => {
        fetchExamples()
    }

    return {data, isLoading, refetch}
}

export default useGetExamples
