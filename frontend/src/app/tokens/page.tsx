'use client'

import Layout from '@/components/layout'
import useGetToken from '@/hooks/tokens/useGetTokens'
import {useEffect, useState} from 'react'
import CreateToken from './CreateToken'
import EditToken from './EditToken'
import CallToAction from '@/components/CallToAction'

const TokensPage = () => {
    const [isCreating, setIsCreating] = useState<boolean>(false)
    const [shouldRefetch, setShouldRefetch] = useState<boolean>(false)
    const {data, errorCode, refetch} = useGetToken()

    useEffect(() => {
        if (shouldRefetch) {
            setIsCreating(false)
            refetch()
            setShouldRefetch(false)
        }
    }, [shouldRefetch])

    return (
        <Layout>
            <section className='flex flex-col'>
                <h1 className='mb-4 text-3xl font-extrabold text-neutral-800'>
                    Token
                </h1>
                <div className='box-border flex w-full flex-col gap-4 rounded-md bg-white p-8 shadow-md'>
                    {errorCode === 404 && !isCreating && (
                        <CallToAction
                            actionLabel='Crear token'
                            onClick={() => setIsCreating(true)}
                            text='La organización no tiene un token asignado.'
                        />
                    )}
                    {isCreating && (
                        <CreateToken setShouldRefetch={setShouldRefetch} />
                    )}
                    {!errorCode && data && (
                        <EditToken
                            token={data?.token}
                            setShouldRefetch={setShouldRefetch}
                        />
                    )}
                </div>
            </section>
        </Layout>
    )
}

export default TokensPage
