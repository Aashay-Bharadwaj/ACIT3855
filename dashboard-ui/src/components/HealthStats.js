import React, { useEffect, useState } from 'react';
import '../App.css';

export default function HealthStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null);

    const getStats = () => {
        fetch(`http://kakfa.eastus2.cloudapp.azure.com:8120/status`)
            .then((res) => res.json())
            .then(
                (result) => {
                    console.log("Received Stats");
                    setStats(result);
                    setIsLoaded(true);
                },
                (error) => {
                    setError(error);
                    setIsLoaded(true);
                }
            );
    };

    useEffect(() => {
        const interval = setInterval(getStats, 20000); // Update every 20 seconds
        return () => clearInterval(interval);
    }, []); // Empty dependency array to run the effect only once on mount

    if (error) {
        console.error("Error found when fetching from API:", error);
        return <div className="error">Error found when fetching from API</div>;
    } else if (!isLoaded) {
        return <div>Loading...</div>;
    } else {
        return (
            <div className="center">
                <h1>Service Status</h1>
                <div>
                    <p><strong>Audit:</strong> {stats['audit']}</p>
                    <p><strong>Storage:</strong> {stats['storage']}</p>
                    <p><strong>Processing:</strong> {stats['processing']}</p>
                    <p><strong>Receiver:</strong> {stats['receiver']}</p>
                    <h3>Last Updated: {stats['last_update']}</h3>
                </div>
            </div>
        );
    }
}
